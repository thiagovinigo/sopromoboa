"""API REST do Só Promo Boa — Agregador de Promoções e Radar de Queda de Preços."""
import os
import secrets
import hashlib
import threading
import time
from typing import List, Optional, Dict, Any
from datetime import datetime

from fastapi import FastAPI, Depends, Query, Header, HTTPException, Response
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, asc

from database import get_db, engine, Base
from models import ProductModel, PriceHistoryModel, StoreModel, AlertModel, ClickModel, AffiliateProgramModel, FavoriteModel
from pricing import is_price_drop_active, is_all_time_low, calculate_discount_percent, DROP_WINDOW_DAYS
from affiliate import build_affiliate_url, create_managed_link, detect_store_from_url
from normalize import clean_title, detect_category, detect_brand
from scraper_worker import run_worker_once

# Inicialização do banco de dados
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Só Promo Boa API",
    description="Backend oficial para agregação de promoções, radar de preços baixos e gestão de links de afiliados.",
    version="1.0.0"
)

# Configuração de CORS
allowed_origins_env = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000")
allowed_origins = [o.strip() for o in allowed_origins_env.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins if "*" not in allowed_origins else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Total-Count"]
)


# ==========================================
# SCHEMAS PYDANTIC
# ==========================================
class PriceHistoryOut(BaseModel):
    price: float
    seen_at: datetime

    class Config:
        from_attributes = True


class DealOut(BaseModel):
    id: str
    title: str
    price: float
    list_price: Optional[float] = None
    previous_price: Optional[float] = None
    lowest_historic_price: Optional[float] = None
    price_dropped: int
    discount_percent: float
    brand: Optional[str] = None
    category: str
    source: str
    image_url: Optional[str] = None
    url: str
    affiliate_url: Optional[str] = None
    coupon_code: Optional[str] = None
    free_shipping: int = 0
    rating: Optional[float] = None
    review_count: int = 0
    is_all_time_low: bool = False
    is_affiliate_deal: int = 0
    is_featured: int = 0
    clicks_count: int = 0
    last_updated: datetime

    class Config:
        from_attributes = True


class DealDetailOut(DealOut):
    price_history: List[PriceHistoryOut] = []
    similar_deals: List[DealOut] = []


class FavoriteRequest(BaseModel):
    product_id: str


class AdminDealCreate(BaseModel):
    title: str
    price: float
    list_price: Optional[float] = None
    source: Optional[str] = None
    url: str
    image_url: Optional[str] = None
    category: Optional[str] = None
    brand: Optional[str] = None
    coupon_code: Optional[str] = None
    is_featured: Optional[int] = 0
    free_shipping: Optional[int] = 1


class AlertCreate(BaseModel):
    search_term: str
    target_price: Optional[float] = None
    min_discount_percent: Optional[float] = None
    category: Optional[str] = None


class AlertOut(BaseModel):
    id: int
    search_term: str
    target_price: Optional[float] = None
    min_discount_percent: Optional[float] = None
    category: Optional[str] = None
    is_active: int
    matched_count: int
    created_at: datetime

    class Config:
        from_attributes = True


class AffiliateProgramCreate(BaseModel):
    name: str
    network_slug: str
    tracking_id: str
    commission_rate: Optional[str] = None


class GenerateLinkRequest(BaseModel):
    url: str
    campaign: Optional[str] = "radar"


# ==========================================
# ENDPOINTS DE OFERTAS & RADAR
# ==========================================
@app.get("/api/deals", response_model=List[DealOut])
def list_deals(
    response: Response,
    q: Optional[str] = Query(None, description="Busca por termo ou marca"),
    category: Optional[str] = Query(None, description="Filtrar por categoria"),
    source: Optional[str] = Query(None, description="Filtrar por loja"),
    only_drops: bool = Query(False, description="Apenas itens que tiveram queda recente"),
    min_discount: Optional[float] = Query(None, description="Desconto percentual mínimo"),
    min_price: Optional[float] = Query(None, description="Preço mínimo"),
    max_price: Optional[float] = Query(None, description="Preço máximo"),
    sort: str = Query("recent", description="recent | drop_desc | discount_desc | price_asc | price_desc"),
    limit: int = Query(24, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """Lista as ofertas com filtros dinâmicos e paginação."""
    query = db.query(ProductModel).filter(ProductModel.is_available == 1)

    if q:
        query = query.filter(ProductModel.title.ilike(f"%{q}%"))
    if category:
        query = query.filter(ProductModel.category == category)
    if source:
        query = query.filter(ProductModel.source.ilike(f"%{source}%"))
    if only_drops:
        query = query.filter(ProductModel.price_dropped == 1)
    if min_discount:
        query = query.filter(ProductModel.discount_percent >= min_discount)
    if min_price is not None:
        query = query.filter(ProductModel.price >= min_price)
    if max_price is not None:
        query = query.filter(ProductModel.price <= max_price)

    # Total de registros correspondentes
    total_count = query.count()
    response.headers["X-Total-Count"] = str(total_count)

    # Ordenação
    if sort == "drop_desc":
        # Ordena pelas maiores diferenças nominais de queda
        query = query.order_by(
            ProductModel.price_dropped.desc(),
            (ProductModel.previous_price - ProductModel.price).desc()
        )
    elif sort == "discount_desc":
        query = query.order_by(ProductModel.discount_percent.desc())
    elif sort == "price_asc":
        query = query.order_by(ProductModel.price.asc())
    elif sort == "price_desc":
        query = query.order_by(ProductModel.price.desc())
    else:
        query = query.order_by(ProductModel.last_updated.desc())

    items = query.offset(offset).limit(limit).all()

    # Preenche flag dinâmico is_all_time_low
    out = []
    for item in items:
        data = DealOut.model_validate(item)
        data.is_all_time_low = is_all_time_low(item.price, item.lowest_historic_price)
        out.append(data)

    return out


@app.get("/api/deals/{product_id}", response_model=DealDetailOut)
def get_deal_detail(product_id: str, db: Session = Depends(get_db)):
    """Retorna detalhes completos do produto, histórico de preços e itens similares."""
    product = db.query(ProductModel).filter(ProductModel.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Produto não encontrado")

    # Histórico de preços ordenado
    history = (
        db.query(PriceHistoryModel)
        .filter(PriceHistoryModel.product_id == product_id)
        .order_by(PriceHistoryModel.seen_at.asc())
        .all()
    )

    # Ofertas similares na mesma categoria
    similar = (
        db.query(ProductModel)
        .filter(
            ProductModel.category == product.category,
            ProductModel.id != product_id,
            ProductModel.is_available == 1
        )
        .order_by(ProductModel.discount_percent.desc())
        .limit(4)
        .all()
    )

    data = DealDetailOut.model_validate(product)
    data.is_all_time_low = is_all_time_low(product.price, product.lowest_historic_price)
    data.price_history = [PriceHistoryOut.model_validate(h) for h in history]
    data.similar_deals = [DealOut.model_validate(s) for s in similar]

    return data


@app.get("/api/radar", response_model=List[DealOut])
def get_radar_deals(db: Session = Depends(get_db)):
    """Retorna as maiores quedas de preço e 'achados' do momento."""
    deals = (
        db.query(ProductModel)
        .filter(
            ProductModel.is_available == 1,
            ProductModel.price_dropped == 1
        )
        .order_by(ProductModel.discount_percent.desc())
        .limit(16)
        .all()
    )

    # Se ainda houver poucos itens com queda histórica recente, complementa com os maiores descontos
    if len(deals) < 8:
        additional = (
            db.query(ProductModel)
            .filter(
                ProductModel.is_available == 1,
                ProductModel.discount_percent > 15
            )
            .order_by(ProductModel.discount_percent.desc())
            .limit(16 - len(deals))
            .all()
        )
        deals.extend([a for a in additional if a.id not in [d.id for d in deals]])

    out = []
    for d in deals:
        item = DealOut.model_validate(d)
        item.is_all_time_low = is_all_time_low(d.price, d.lowest_historic_price)
        out.append(item)

    return out


# ==========================================
# ENDPOINT DE REDIRECIONAMENTO COMISSIONADO
# ==========================================
@app.get("/r/{product_id}")
def redirect_to_deal(product_id: str, db: Session = Depends(get_db)):
    """Redirecionamento rastreado com tag de afiliado para a loja original."""
    product = db.query(ProductModel).filter(ProductModel.id == product_id).first()
    if not product:
        # Fallback gracioso para a vitrine caso o produto não exista
        return RedirectResponse(url="http://localhost:3000/radar", status_code=307)

    # Incrementa contador de cliques no anúncio
    product.clicks_count = (product.clicks_count or 0) + 1

    # Registra o clique para métricas de conversão
    try:
        db.add(ClickModel(
            product_id=product_id,
            source=product.source,
            created_at=datetime.utcnow()
        ))
        db.commit()
    except Exception:
        pass

    target_url = product.affiliate_url or product.url
    if not target_url or not target_url.startswith("http"):
        import urllib.parse
        store_q = product.source or "oferta"
        target_url = f"https://www.google.com/search?q={urllib.parse.quote_plus(product.title + ' ' + store_q)}"

    return RedirectResponse(url=target_url, status_code=307)


# ==========================================
# CATEGORIAS & LOJAS
# ==========================================
@app.get("/api/categories")
def get_categories(db: Session = Depends(get_db)):
    """Retorna todas as categorias ativas com quantidade de ofertas."""
    counts = (
        db.query(ProductModel.category, func.count(ProductModel.id))
        .filter(ProductModel.is_available == 1)
        .group_by(ProductModel.category)
        .all()
    )
    labels = {
        "smartphones": "Smartphones & Celulares",
        "informatica": "Informática & PCs",
        "eletronicos": "Eletrônicos & TV",
        "games": "Games & Consoles",
        "eletrodomesticos": "Eletrodomésticos",
        "casa": "Casa & Cozinha",
        "geral": "Geral & Outros"
    }
    return [
        {"slug": cat, "name": labels.get(cat, cat.title()), "total_deals": count}
        for cat, count in counts if cat
    ]


@app.get("/api/stores")
def get_stores(db: Session = Depends(get_db)):
    """Retorna as lojas monitoradas e o volume de produtos em promoção."""
    stores = db.query(StoreModel).filter(StoreModel.is_active == 1).all()
    out = []
    for s in stores:
        actual_deals = (
            db.query(ProductModel)
            .filter(ProductModel.source.ilike(f"%{s.name}%"), ProductModel.is_available == 1)
            .count()
        )
        out.append({
            "slug": s.slug,
            "name": s.name,
            "total_deals": actual_deals if actual_deals > 0 else (s.total_deals or 0),
            "affiliate_network": s.affiliate_network,
            "logo_url": s.logo_url
        })
    return out


# ==========================================
# ALERTAS DE PREÇO (PRIVACIDADE POR TOKEN)
# ==========================================
@app.post("/api/alerts")
def create_alert(
    alert_in: AlertCreate,
    x_alert_token: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """Cria um alerta de preço vinculado ao token do navegador do usuário."""
    manage_token = x_alert_token
    if not manage_token:
        # Gera novo token criptográfico de 256 bits
        manage_token = secrets.token_hex(32)

    token_hash = hashlib.sha256(manage_token.encode("utf-8")).hexdigest()

    new_alert = AlertModel(
        owner_token_hash=token_hash,
        search_term=alert_in.search_term,
        target_price=alert_in.target_price,
        min_discount_percent=alert_in.min_discount_percent,
        category=alert_in.category,
        is_active=1,
        created_at=datetime.utcnow()
    )
    db.add(new_alert)
    db.commit()
    db.refresh(new_alert)

    return {
        "success": True,
        "alert": AlertOut.model_validate(new_alert),
        "manage_token": manage_token
    }


@app.get("/api/alerts", response_model=List[AlertOut])
def list_my_alerts(
    x_alert_token: str = Header(..., description="Token de gestão de alertas do navegador"),
    db: Session = Depends(get_db)
):
    """Lista todos os alertas associados ao token do usuário."""
    token_hash = hashlib.sha256(x_alert_token.encode("utf-8")).hexdigest()
    alerts = (
        db.query(AlertModel)
        .filter(AlertModel.owner_token_hash == token_hash, AlertModel.is_active == 1)
        .order_by(AlertModel.created_at.desc())
        .all()
    )
    return [AlertOut.model_validate(a) for a in alerts]


@app.delete("/api/alerts/{alert_id}")
def delete_alert(
    alert_id: int,
    x_alert_token: str = Header(..., description="Token de gestão de alertas do navegador"),
    db: Session = Depends(get_db)
):
    """Remove um alerta criado pelo usuário."""
    token_hash = hashlib.sha256(x_alert_token.encode("utf-8")).hexdigest()
    alert = (
        db.query(AlertModel)
        .filter(AlertModel.id == alert_id, AlertModel.owner_token_hash == token_hash)
        .first()
    )
    if not alert:
        raise HTTPException(status_code=404, detail="Alerta não encontrado ou acesso não autorizado")

    db.delete(alert)
    db.commit()
    return {"success": True, "message": "Alerta removido com sucesso"}


# ==========================================
# GESTÃO DE PROGRAMAS DE AFILIADOS & GERADOR DE LINKS
# ==========================================
@app.get("/api/affiliates")
def get_affiliate_programs(db: Session = Depends(get_db)):
    """Lista todos os programas de afiliados e suas tags cadastradas."""
    programs = db.query(AffiliateProgramModel).all()
    return [
        {
            "id": p.id,
            "name": p.name,
            "network_slug": p.network_slug,
            "tracking_id": p.tracking_id,
            "commission_rate": p.commission_rate,
            "status": p.status
        }
        for p in programs
    ]


@app.post("/api/affiliates")
def upsert_affiliate_program(program_in: AffiliateProgramCreate, db: Session = Depends(get_db)):
    """Cadastra ou atualiza um programa de afiliado com tag de comissão."""
    program = db.query(AffiliateProgramModel).filter(AffiliateProgramModel.network_slug == program_in.network_slug).first()
    if program:
        program.tracking_id = program_in.tracking_id
        program.name = program_in.name
        program.commission_rate = program_in.commission_rate
        program.updated_at = datetime.utcnow()
    else:
        program = AffiliateProgramModel(
            name=program_in.name,
            network_slug=program_in.network_slug,
            tracking_id=program_in.tracking_id,
            commission_rate=program_in.commission_rate,
            status="active"
        )
        db.add(program)

    db.commit()
    return {"success": True, "message": f"Programa '{program_in.name}' salvo com sucesso!"}


@app.post("/api/affiliates/generate")
def generate_affiliate_link(req: GenerateLinkRequest, db: Session = Depends(get_db)):
    """Gerador universal de links de afiliados com rastreamento UTM."""
    store = detect_store_from_url(req.url)
    program = db.query(AffiliateProgramModel).filter(AffiliateProgramModel.network_slug == store).first()
    custom_tag = program.tracking_id if program else None

    result = create_managed_link(req.url, campaign_name=req.campaign, custom_tag=custom_tag)
    return result


# ==========================================
# FAVORITOS (MOMENTO 1 - USUÁRIO COMUM)
# ==========================================
@app.get("/api/favorites", response_model=List[DealOut])
def list_favorites(
    x_user_token: str = Header(..., description="Token anônimo do usuário no localStorage"),
    db: Session = Depends(get_db)
):
    """Retorna os produtos favoritados pelo usuário com status de preço atualizado."""
    token_hash = hashlib.sha256(x_user_token.encode("utf-8")).hexdigest()
    fav_ids = [
        f.product_id for f in db.query(FavoriteModel)
        .filter(FavoriteModel.user_token_hash == token_hash)
        .order_by(FavoriteModel.created_at.desc())
        .all()
    ]
    if not fav_ids:
        return []

    items = db.query(ProductModel).filter(ProductModel.id.in_(fav_ids)).all()
    out = []
    for item in items:
        data = DealOut.model_validate(item)
        data.is_all_time_low = is_all_time_low(item.price, item.lowest_historic_price)
        out.append(data)
    return out


@app.get("/api/favorites/ids")
def get_favorite_ids(
    x_user_token: str = Header(..., description="Token do usuário"),
    db: Session = Depends(get_db)
):
    """Retorna apenas a lista de IDs de produtos favoritados pelo usuário."""
    token_hash = hashlib.sha256(x_user_token.encode("utf-8")).hexdigest()
    favs = db.query(FavoriteModel.product_id).filter(FavoriteModel.user_token_hash == token_hash).all()
    return [f[0] for f in favs]


@app.post("/api/favorites")
def toggle_favorite(
    req: FavoriteRequest,
    x_user_token: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """Adiciona ou remove um produto dos favoritos do usuário (toggle)."""
    user_token = x_user_token or secrets.token_hex(32)
    token_hash = hashlib.sha256(user_token.encode("utf-8")).hexdigest()

    existing = db.query(FavoriteModel).filter(
        FavoriteModel.user_token_hash == token_hash,
        FavoriteModel.product_id == req.product_id
    ).first()

    is_favorited = False
    if existing:
        db.delete(existing)
        db.commit()
    else:
        fav = FavoriteModel(user_token_hash=token_hash, product_id=req.product_id, created_at=datetime.utcnow())
        db.add(fav)
        db.commit()
        is_favorited = True

    return {
        "success": True,
        "is_favorited": is_favorited,
        "user_token": user_token,
        "product_id": req.product_id
    }


@app.delete("/api/favorites/{product_id}")
def remove_favorite(
    product_id: str,
    x_user_token: str = Header(...),
    db: Session = Depends(get_db)
):
    """Remove um produto da lista de favoritos."""
    token_hash = hashlib.sha256(x_user_token.encode("utf-8")).hexdigest()
    fav = db.query(FavoriteModel).filter(
        FavoriteModel.user_token_hash == token_hash,
        FavoriteModel.product_id == product_id
    ).first()
    if fav:
        db.delete(fav)
        db.commit()
    return {"success": True, "message": "Favorito removido"}


# ==========================================
# PAINEL DE ADMINISTRAÇÃO & MONETIZAÇÃO (MOMENTO 2)
# ==========================================
@app.get("/api/admin/deals", response_model=List[DealOut])
def list_admin_affiliate_deals(db: Session = Depends(get_db)):
    """Lista todos os anúncios cadastrados por nós com links de afiliados."""
    deals = (
        db.query(ProductModel)
        .filter(ProductModel.is_affiliate_deal == 1)
        .order_by(ProductModel.created_at.desc())
        .all()
    )
    out = []
    for d in deals:
        item = DealOut.model_validate(d)
        item.is_all_time_low = is_all_time_low(d.price, d.lowest_historic_price)
        out.append(item)
    return out


@app.post("/api/admin/deals", response_model=DealOut)
def create_admin_affiliate_deal(deal_in: AdminDealCreate, db: Session = Depends(get_db)):
    """Publica um anúncio no painel admin com link de afiliado e tag injetada."""
    now = datetime.utcnow()
    title = clean_title(deal_in.title)
    store = deal_in.source or detect_store_from_url(deal_in.url).capitalize()
    cat = deal_in.category or detect_category(title)
    brand = deal_in.brand or detect_brand(title)

    # Injeta a tag de afiliado configurada para a loja
    store_slug = store.lower()
    program = db.query(AffiliateProgramModel).filter(AffiliateProgramModel.network_slug == store_slug).first()
    custom_tag = program.tracking_id if program else None
    affiliate_url = build_affiliate_url(deal_in.url, store_slug=store_slug, custom_tag=custom_tag)

    deal_id = f"aff_{hashlib.md5(deal_in.url.encode('utf-8')).hexdigest()[:12]}"
    discount = calculate_discount_percent(deal_in.price, list_price=deal_in.list_price)

    new_prod = ProductModel(
        id=deal_id,
        title=title,
        price=deal_in.price,
        list_price=deal_in.list_price,
        previous_price=deal_in.list_price if (deal_in.list_price and deal_in.list_price > deal_in.price) else None,
        lowest_historic_price=deal_in.price,
        price_dropped=1 if (deal_in.list_price and deal_in.list_price > deal_in.price) else 0,
        discount_percent=discount,
        brand=brand,
        category=cat,
        url=deal_in.url,
        affiliate_url=affiliate_url,
        source=store,
        image_url=deal_in.image_url or "",
        is_available=1,
        coupon_code=deal_in.coupon_code,
        free_shipping=deal_in.free_shipping or 0,
        is_affiliate_deal=1,
        is_featured=deal_in.is_featured or 0,
        rating=5.0,
        review_count=0,
        clicks_count=0,
        created_at=now,
        last_updated=now,
        price_changed_at=now,
    )
    db.merge(new_prod)
    db.add(PriceHistoryModel(product_id=deal_id, price=deal_in.price, seen_at=now))
    db.commit()

    item = DealOut.model_validate(new_prod)
    item.is_all_time_low = True
    return item


@app.delete("/api/admin/deals/{product_id}")
def delete_admin_deal(product_id: str, db: Session = Depends(get_db)):
    """Remove um anúncio de afiliado cadastrado pelo administrador."""
    prod = db.query(ProductModel).filter(ProductModel.id == product_id).first()
    if not prod:
        raise HTTPException(status_code=404, detail="Anúncio não encontrado")
    db.delete(prod)
    db.commit()
    return {"success": True, "message": "Anúncio removido"}


@app.get("/api/admin/stats")
def get_admin_monetization_stats(db: Session = Depends(get_db)):
    """Retorna métricas consolidadas de cliques, conversão e desempenho dos anúncios afiliados."""
    total_clicks = db.query(ClickModel).count()
    affiliate_deals_count = db.query(ProductModel).filter(ProductModel.is_affiliate_deal == 1).count()
    total_deals = db.query(ProductModel).filter(ProductModel.is_available == 1).count()

    clicks_by_store = (
        db.query(ClickModel.source, func.count(ClickModel.id))
        .group_by(ClickModel.source)
        .order_by(desc(func.count(ClickModel.id)))
        .all()
    )

    top_clicked = (
        db.query(ProductModel)
        .filter(ProductModel.clicks_count > 0)
        .order_by(desc(ProductModel.clicks_count))
        .limit(6)
        .all()
    )

    return {
        "total_clicks": total_clicks,
        "affiliate_deals_count": affiliate_deals_count,
        "total_deals_monitored": total_deals,
        "clicks_by_store": [{"store": s, "clicks": c} for s, c in clicks_by_store],
        "top_clicked_deals": [
            {"id": p.id, "title": p.title, "clicks": p.clicks_count, "price": p.price, "source": p.source}
            for p in top_clicked
        ]
    }


# ==========================================
# AGENDAMENTO E EXECUÇÃO AUTOMÁTICA DO WORKER
# ==========================================
worker_state = {
    "is_running": False,
    "last_run": None,
    "last_stats": None,
    "history": [],
}


def background_worker_loop():
    """Executa a raspagem autônoma de ofertas em background a cada 15 minutos."""
    time.sleep(5)
    while True:
        try:
            start_t = time.time()
            worker_state["is_running"] = True
            print("[AutoWorker] Executando varredura autônoma periódica...")
            stats = run_worker_once()
            duration = round(time.time() - start_t, 2)
            now_iso = datetime.utcnow().isoformat()
            worker_state["last_run"] = now_iso
            worker_state["last_stats"] = stats
            worker_state["history"].insert(0, {
                "timestamp": now_iso,
                "stats": stats,
                "duration_seconds": duration,
                "type": "scheduled"
            })
            worker_state["history"] = worker_state["history"][:20]
        except Exception as e:
            print(f"[AutoWorker] Erro na execução periódica: {e}")
        finally:
            worker_state["is_running"] = False
        time.sleep(15 * 60) # 15 minutos


@app.on_event("startup")
def start_auto_worker_on_startup():
    """Inicia thread de background para o worker na subida da aplicação."""
    t = threading.Thread(target=background_worker_loop, daemon=True)
    t.start()


@app.post("/api/worker/run")
def trigger_worker_run():
    """Dispara uma execução sob demanda do scraper worker em background thread."""
    if worker_state["is_running"]:
        return {"success": False, "message": "O worker já está executando uma varredura neste momento!"}

    def _run():
        start_t = time.time()
        worker_state["is_running"] = True
        try:
            stats = run_worker_once()
            duration = round(time.time() - start_t, 2)
            now_iso = datetime.utcnow().isoformat()
            worker_state["last_run"] = now_iso
            worker_state["last_stats"] = stats
            worker_state["history"].insert(0, {
                "timestamp": now_iso,
                "stats": stats,
                "duration_seconds": duration,
                "type": "manual"
            })
            worker_state["history"] = worker_state["history"][:20]
        finally:
            worker_state["is_running"] = False

    thread = threading.Thread(target=_run, daemon=True)
    thread.start()
    return {"success": True, "message": "Scraper worker disparado em segundo plano!"}


@app.post("/api/worker/simulate-drop")
def simulate_price_drop(db: Session = Depends(get_db)):
    """Simula uma queda real de preço para homologar o Radar de Quedas e os Alertas."""
    product = (
        db.query(ProductModel)
        .filter(ProductModel.is_available == 1)
        .order_by(func.random())
        .first()
    )
    if not product:
        raise HTTPException(status_code=404, detail="Nenhum produto cadastrado para simular")

    now = datetime.utcnow()
    old_price = product.price
    new_price = round(old_price * 0.82, 2)

    product.previous_price = old_price
    product.price = new_price
    product.price_dropped = 1
    product.price_changed_at = now
    product.last_updated = now

    if product.lowest_historic_price is None or new_price < product.lowest_historic_price:
        product.lowest_historic_price = new_price

    product.discount_percent = calculate_discount_percent(
        new_price,
        list_price=product.list_price,
        previous_price=old_price
    )

    db.add(PriceHistoryModel(
        product_id=product.id,
        price=new_price,
        seen_at=now
    ))

    matched_alerts = 0
    active_alerts = db.query(AlertModel).filter(AlertModel.is_active == 1).all()
    for alert in active_alerts:
        if alert.search_term.lower() in product.title.lower():
            if alert.target_price is None or new_price <= alert.target_price:
                alert.matched_count = (alert.matched_count or 0) + 1
                alert.last_notified_at = now
                matched_alerts += 1

    db.commit()

    return {
        "success": True,
        "message": f"Queda simulada com sucesso para '{product.title}'!",
        "deal": {
            "id": product.id,
            "title": product.title,
            "old_price": old_price,
            "new_price": new_price,
            "discount_percent": product.discount_percent,
            "matched_alerts": matched_alerts
        }
    }


@app.get("/api/worker/status")
def get_worker_status(db: Session = Depends(get_db)):
    """Retorna o status atual do worker, última execução e estatísticas."""
    total_prods = db.query(ProductModel).filter(ProductModel.is_available == 1).count()
    total_drops = db.query(ProductModel).filter(ProductModel.price_dropped == 1).count()

    return {
        "is_running": worker_state["is_running"],
        "last_run": worker_state["last_run"],
        "last_stats": worker_state["last_stats"],
        "history": worker_state.get("history", []),
        "interval_minutes": 15,
        "total_monitored": total_prods,
        "total_active_drops": total_drops,
        "active_scrapers": [
            {"name": "Gatry Real Deals (Páginas 1 a 4)", "target": "Amazon, Magalu, ML, KaBuM", "status": "Ativo", "interval": "15 min"},
            {"name": "Curated Golden Deals", "target": "Top 32 Ofertas Auditadas", "status": "Ativo", "interval": "15 min"},
            {"name": "Targeted Price Tracker", "target": "Histórico & Alertas de Usuários", "status": "Ativo", "interval": "Contínuo"},
        ]
    }


@app.get("/api/health")
def health_check():
    return {"status": "ok", "app": "SoPromoBoa", "timestamp": datetime.utcnow()}
