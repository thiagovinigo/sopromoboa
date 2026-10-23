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
import re
import urllib.parse
from sqlalchemy import func, desc, asc, or_

from database import get_db, engine, Base
from models import ProductModel, PriceHistoryModel, StoreModel, AlertModel, ClickModel, AffiliateProgramModel, FavoriteModel, DiscoveredStoreModel
from pricing import is_price_drop_active, is_all_time_low, calculate_discount_percent, DROP_WINDOW_DAYS
from affiliate import build_affiliate_url, create_managed_link, detect_store_from_url
from normalize import clean_title, detect_category, detect_brand
from scraper_worker import run_worker_once
from store_hunter_agent import StoreHunterAgent

# Inicialização do banco de dados
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Só Promo Boa API",
    description="Backend oficial para agregação de promoções, radar de preços baixos e gestão de links de afiliados.",
    version="1.0.0"
)

# Configuração de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
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
    is_lightning_deal: int = 0
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
    is_lightning_deal: Optional[int] = 0
    free_shipping: Optional[int] = 1


class QuickImportRequest(BaseModel):
    url: str
    category: Optional[str] = None
    custom_title: Optional[str] = None
    custom_price: Optional[float] = None
    custom_list_price: Optional[float] = None
    image_url: Optional[str] = None
    coupon_code: Optional[str] = None
    is_lightning: Optional[bool] = True
    is_featured: Optional[bool] = True


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
    campaign: Optional[str] = "redes_sociais"


class StorePriceComparison(BaseModel):
    store: str
    price: float
    deal_id: str
    product_title: str
    url: str
    affiliate_url: Optional[str] = None
    image_url: Optional[str] = None
    is_lowest: bool = False
    price_diff: float = 0.0
    free_shipping: int = 0


class WorkerSearchResult(BaseModel):
    query: str
    total_found: int
    best_price: Optional[float] = None
    max_price: Optional[float] = None
    average_price: Optional[float] = None
    potential_savings: Optional[float] = None
    best_store: Optional[str] = None
    did_you_mean: Optional[str] = None
    did_you_mean_notice: Optional[str] = None
    stores_comparison: List[StorePriceComparison] = []
    items: List[DealOut] = []


# ==========================================
# BUSCA PERSONALIZADA & COMPARADOR MULTI-LOJAS
# ==========================================
@app.get("/api/comparator/search", response_model=WorkerSearchResult)
def comparator_search(
    q: str = Query(..., min_length=2, description="Nome do produto para busca personalizada"),
    db: Session = Depends(get_db)
):
    """Busca personalizada inteligente com normalização de termos, desambiguação de modelos e ranking multi-lojas."""
    raw_q = q.strip()
    q_norm = raw_q.lower()

    STOPWORDS = {"de", "da", "do", "dos", "das", "com", "para", "pra", "em", "no", "na", "o", "a", "os", "as", "e", "por", "ate", "até"}
    UNIT_WORDS = {"polegadas", "polegada", "pol", "pols", "inches", "inch", "gb", "tb", "giga", "gigas", "mb", "hz", "w", "watts", "v", "volts"}
    ACCESSORY_KEYWORDS = {"suporte", "braço", "braco", "articulado", "capa", "capinha", "pelicula", "película", "cabo", "adaptador", "carregador"}

    # 1. Dicionário de Aliases e Typos Frequentes
    COMMON_ALIASES = {
        "iphone5": ("iphone 15", "O iPhone 5 é um modelo descontinuado pelas lojas oficiais. Nossos workers buscaram as melhores ofertas do iPhone 15:"),
        "iphone 5": ("iphone 15", "O iPhone 5 é um modelo descontinuado pelas lojas oficiais. Nossos workers buscaram as melhores ofertas do iPhone 15:"),
        "ps5": ("playstation 5", None),
        "playstation5": ("playstation 5", None),
        "ps4": ("playstation 4", None),
        "airfryer": ("air fryer", None),
        "s24": ("galaxy s24", None),
        "s23": ("galaxy s23", None),
        "rtx4060": ("rtx 4060", None),
        "rtx3060": ("rtx 3060", None),
        "switch": ("nintendo switch", None),
    }

    did_you_mean = None
    did_you_mean_notice = None
    target_query = raw_q

    if q_norm in COMMON_ALIASES:
        target_query, did_you_mean_notice = COMMON_ALIASES[q_norm]
        did_you_mean = target_query
    else:
        # Separa aspas de polegadas e números colados (ex: 32" -> 32 ", 32pol -> 32 pol)
        target_query = target_query.replace('"', ' " ').replace("'", " ' ")
        target_query = re.sub(r"([a-zA-Z]{2,})(\d+)", r"\1 \2", target_query)
        target_query = re.sub(r"(\d+)([a-zA-Z]{2,})", r"\1 \2", target_query)

    # Identifica se o usuário quer explicitamente um acessório
    user_wants_accessory = any(ak in q_norm for ak in ACCESSORY_KEYWORDS)

    raw_tokens = [t.lower().strip() for t in re.split(r"[\s\-_/]+", target_query) if t.strip()]

    # Separa tokens de busca eliminando stopwords e unidades de medida puras
    clean_tokens = []
    numeric_tokens = []
    for t in raw_tokens:
        if t in STOPWORDS or t in {'"', "'"}:
            continue
        if t in UNIT_WORDS or t.startswith("poleg") or t.startswith("pol."):
            # Unidades de medida (ex: 'polegadas', 'polegads', 'pol') não devem ser termos obrigatórios no título
            continue
        if t.isdigit():
            numeric_tokens.append(t)
            clean_tokens.append(t)
        else:
            clean_tokens.append(t)

    if not clean_tokens and raw_tokens:
        clean_tokens = [t for t in raw_tokens if t not in STOPWORDS]

    # 2. Busca preliminar ampla no banco
    candidates_query = db.query(ProductModel).filter(ProductModel.is_available == 1)
    
    # Usa o token de texto principal mais longo para filtrar no SQL
    text_tokens = [t for t in clean_tokens if not t.isdigit() and len(t) > 2]
    lead_token = text_tokens[0] if text_tokens else (clean_tokens[0] if clean_tokens else "")
    if lead_token:
        candidates_query = candidates_query.filter(ProductModel.title.ilike(f"%{lead_token}%"))

    all_candidates = candidates_query.all()

    # 3. Filtragem rigorosa em memória
    matches = []
    for p in all_candidates:
        title_lower = p.title.lower()

        # Se o usuário não pediu suporte/acessório, descarta suportes de monitor/braço articulado
        if not user_wants_accessory:
            if title_lower.startswith("suporte ") or "suporte articulado" in title_lower or "suporte de mesa" in title_lower or "suporte para monitor" in title_lower:
                continue

        is_match = True
        for t in clean_tokens:
            if t.isdigit():
                # Para números de modelo ou dimensão (ex: '32', '24', '15'),
                # aceita limites de palavras ou sufixo de unidade (" , ' , pol)
                pattern = rf"\b{re.escape(t)}(\"|\'|pol|p|\b)"
                if not re.search(pattern, title_lower):
                    is_match = False
                    break
            else:
                if t not in title_lower:
                    is_match = False
                    break
        if is_match:
            matches.append(p)

    # Ordena pelo menor preço
    matches.sort(key=lambda x: x.price)

    # 4. Agrupa por loja (source) para identificar o melhor preço de cada marketplace
    store_deals: Dict[str, ProductModel] = {}
    for p in matches:
        s = p.source or "Outros"
        if s not in store_deals or p.price < store_deals[s].price:
            store_deals[s] = p

    items_out = [DealOut.model_validate(p) for p in matches[:60]]
    for d in items_out:
        d.is_all_time_low = is_all_time_low(d.price, d.lowest_historic_price)

    if store_deals:
        all_prices = [p.price for p in store_deals.values()]
        best_price = min(all_prices)
        max_price = max(all_prices)
        avg_price = round(sum(all_prices) / len(all_prices), 2)
        savings = round(max_price - best_price, 2)
        best_store = None

        comparison_list = []
        for store_name, p in store_deals.items():
            is_low = (p.price == best_price)
            if is_low and not best_store:
                best_store = store_name
            diff = round(p.price - best_price, 2)
            comparison_list.append(StorePriceComparison(
                store=store_name,
                price=p.price,
                deal_id=p.id,
                product_title=p.title,
                url=p.url,
                affiliate_url=p.affiliate_url or p.url,
                image_url=p.image_url,
                is_lowest=is_low,
                price_diff=diff,
                free_shipping=p.free_shipping or 0
            ))

        comparison_list.sort(key=lambda x: x.price)

        return WorkerSearchResult(
            query=raw_q,
            total_found=len(matches),
            best_price=best_price,
            max_price=max_price,
            average_price=avg_price,
            potential_savings=savings,
            best_store=best_store,
            did_you_mean=did_you_mean,
            did_you_mean_notice=did_you_mean_notice,
            stores_comparison=comparison_list,
            items=items_out
        )
    else:
        # Fallback de busca comissionada nos principais varejistas
        q_enc = urllib.parse.quote_plus(raw_q)
        words_slug = [w for w in re.split(r"\s+", target_query) if len(w) > 1]
        q_slug = urllib.parse.quote_plus("-".join(words_slug).lower())

        fallback_stores = [
            ("Amazon", f"https://www.amazon.com.br/s?k={q_enc}&tag=sopromoboa-20"),
            ("Mercado Livre", f"https://lista.mercadolivre.com.br/{q_slug}?matt_tool=sopromoboa_ml"),
            ("Magazine Luiza", f"https://www.magazineluiza.com.br/busca/{q_slug}/?parceiro=sopromoboa"),
            ("KaBuM!", f"https://www.kabum.com.br/busca/{q_slug}?tag=sopromoboa"),
            ("Shopee", f"https://shopee.com.br/search?keyword={q_enc}&af_siteid=sopromoboa_sp"),
        ]

        comparison_list = [
            StorePriceComparison(
                store=s_name,
                price=0.0,
                deal_id=f"search_{s_name.lower().replace(' ', '_')}",
                product_title=f"Buscar '{raw_q}' na loja oficial {s_name}",
                url=s_url,
                affiliate_url=s_url,
                image_url=None,
                is_lowest=False,
                price_diff=0.0,
                free_shipping=1
            )
            for s_name, s_url in fallback_stores
        ]

        return WorkerSearchResult(
            query=raw_q,
            total_found=0,
            best_price=None,
            max_price=None,
            average_price=None,
            potential_savings=None,
            best_store=None,
            did_you_mean=did_you_mean,
            did_you_mean_notice=did_you_mean_notice,
            stores_comparison=comparison_list,
            items=[]
        )


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


@app.get("/api/deals/lightning", response_model=List[DealOut])
def list_lightning_deals(
    response: Response,
    q: Optional[str] = Query(None, description="Busca por termo ou marca"),
    category: Optional[str] = Query(None, description="Filtrar por nicho"),
    min_discount: Optional[float] = Query(None, description="Desconto mínimo"),
    sort: str = Query("discount_desc", description="discount_desc | recent | price_asc | price_desc"),
    limit: int = Query(24, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """Retorna ofertas relâmpago detectadas por robôs ou cadastradas com super descontos."""
    query = db.query(ProductModel).filter(
        ProductModel.is_available == 1,
        or_(ProductModel.is_lightning_deal == 1, ProductModel.discount_percent >= 25.0)
    )

    if q:
        query = query.filter(ProductModel.title.ilike(f"%{q}%"))
    if category and category != "todas":
        query = query.filter(ProductModel.category == category)
    if min_discount:
        query = query.filter(ProductModel.discount_percent >= min_discount)

    total_count = query.count()
    response.headers["X-Total-Count"] = str(total_count)

    if sort == "discount_desc":
        query = query.order_by(ProductModel.discount_percent.desc())
    elif sort == "price_asc":
        query = query.order_by(ProductModel.price.asc())
    elif sort == "price_desc":
        query = query.order_by(ProductModel.price.desc())
    else:
        query = query.order_by(ProductModel.last_updated.desc())

    items = query.offset(offset).limit(limit).all()

    out = []
    for item in items:
        data = DealOut.model_validate(item)
        data.is_all_time_low = is_all_time_low(item.price, item.lowest_historic_price)
        data.is_lightning_deal = 1
        out.append(data)

    return out


@app.post("/api/deals/lightning/scan")
def trigger_lightning_scan(db: Session = Depends(get_db)):
    """Robô varredor de ofertas relâmpago: audita o catálogo e promove itens com super desconto."""
    now = datetime.utcnow()
    # 1. Marca produtos com desconto >= 25%
    db.query(ProductModel).filter(ProductModel.discount_percent >= 25.0).update(
        {ProductModel.is_lightning_deal: 1}, synchronize_session=False
    )
    # 2. Assegura que produtos emblemáticos das marcas mais procuradas estejam marcados
    flagship_terms = ["fire tv", "echo", "kindle", "creatina", "whey", "air fryer", "iphone", "galaxy s", "jbl"]
    for term in flagship_terms:
        db.query(ProductModel).filter(ProductModel.title.ilike(f"%{term}%"), ProductModel.discount_percent >= 15.0).update(
            {ProductModel.is_lightning_deal: 1}, synchronize_session=False
        )

    db.commit()
    total_lightning = db.query(ProductModel).filter(ProductModel.is_lightning_deal == 1, ProductModel.is_available == 1).count()
    return {
        "success": True,
        "message": f"Robôs de Ofertas Relâmpago finalizaram a auditoria. {total_lightning} ofertas ativas!",
        "total_active_lightning": total_lightning,
        "scanned_at": now.isoformat()
    }


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


@app.get("/api/worker/search", response_model=WorkerSearchResult)
def worker_search_deals(
    q: str = Query(..., min_length=2, description="Termo do produto a ser caçado pelos workers"),
    max_price: Optional[float] = Query(None, description="Preço máximo desejado"),
    min_price: Optional[float] = Query(None, description="Preço mínimo desejado"),
    source: Optional[str] = Query(None, description="Filtrar por loja específica"),
    sort: str = Query("price_asc", description="price_asc | discount_desc | recent"),
    limit: int = Query(40, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Aciona a busca inteligente dos workers para caçar o melhor preço de um item entre lojas."""
    query = db.query(ProductModel).filter(ProductModel.is_available == 1)

    # Limpeza e tokenização dos termos
    raw_terms = [t.strip() for t in q.replace("-", " ").replace("+", " ").split() if len(t.strip()) > 1]

    if raw_terms:
        from sqlalchemy import and_, or_
        and_conditions = [ProductModel.title.ilike(f"%{term}%") for term in raw_terms]
        matched_query = query.filter(and_(*and_conditions))

        # Se houver menos de 2 resultados com AND estrito, relaxa para OR
        if matched_query.count() < 2:
            or_conditions = [ProductModel.title.ilike(f"%{term}%") for term in raw_terms]
            query = query.filter(or_(*or_conditions))
        else:
            query = matched_query

    if source:
        query = query.filter(ProductModel.source.ilike(f"%{source}%"))
    if max_price is not None:
        query = query.filter(ProductModel.price <= max_price)
    if min_price is not None:
        query = query.filter(ProductModel.price >= min_price)

    if sort == "discount_desc":
        query = query.order_by(ProductModel.discount_percent.desc())
    elif sort == "recent":
        query = query.order_by(ProductModel.last_updated.desc())
    else: # price_asc (menor preço primeiro)
        query = query.order_by(ProductModel.price.asc())

    all_matches = query.limit(limit).all()

    if not all_matches:
        return WorkerSearchResult(
            query=q,
            total_found=0,
            best_price=None,
            max_price=None,
            average_price=None,
            potential_savings=None,
            stores_comparison=[],
            items=[]
        )

    prices = [p.price for p in all_matches]
    best_p = min(prices)
    max_p = max(prices)
    avg_p = round(sum(prices) / len(prices), 2)
    savings = round(max_p - best_p, 2) if len(prices) > 1 else round(best_p * 0.15, 2)

    # Comparação consolidada de melhor preço por loja
    store_map = {}
    for p in all_matches:
        if p.source not in store_map or p.price < store_map[p.source]["price"]:
            store_map[p.source] = {
                "store": p.source,
                "price": p.price,
                "deal_id": p.id,
                "product_title": p.title,
                "url": p.affiliate_url or p.url
            }

    stores_comp = [
        StorePriceComparison(
            store=data["store"],
            price=data["price"],
            deal_id=data["deal_id"],
            product_title=data["product_title"],
            url=data["url"]
        )
        for data in sorted(store_map.values(), key=lambda x: x["price"])
    ]

    out_items = []
    for item in all_matches:
        data = DealOut.model_validate(item)
        data.is_all_time_low = is_all_time_low(item.price, item.lowest_historic_price)
        out_items.append(data)

    return WorkerSearchResult(
        query=q,
        total_found=len(all_matches),
        best_price=best_p,
        max_price=max_p,
        average_price=avg_p,
        potential_savings=savings,
        stores_comparison=stores_comp,
        items=out_items
    )


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

    # Busca tag dinâmica cadastrada no banco de dados para a Amazon
    amazon_prog = db.query(AffiliateProgramModel).filter(AffiliateProgramModel.network_slug == "amazon").first()
    amazon_tag = amazon_prog.tracking_id if (amazon_prog and amazon_prog.tracking_id) else "quepromo-20"

    # Se a URL for inválida ou um identificador interno de teste, resolve automaticamente para busca direta na loja
    markers = [
        "/dp/ama_", "/p/mer_", "/produto/mag_", "/produto/kab_",
        "/product/sho_", "/cas_", "/produto/tool_", "/produto/perf_",
        "/produto/hw_", "/produto/info_", "/produto/game_", "/produto/eletro_",
        "/produto/casa_", "/produto/sport_", "/produto/hlth_", "/produto/book_"
    ]
    is_placeholder = any(m in (target_url or "") for m in markers)

    if not target_url or not target_url.startswith("http") or is_placeholder:
        import urllib.parse
        import re
        clean_title = re.sub(r"[—\-\(\)\/\,\.\:\+]", " ", product.title)
        clean_title = re.sub(r"\s+", " ", clean_title).strip()
        words = clean_title.split()[:7]
        search_term = " ".join(words)
        q = urllib.parse.quote_plus(search_term)
        q_slug = urllib.parse.quote_plus("-".join(words).lower())
        s = (product.source or "").lower()

        if "amazon" in s:
            target_url = f"https://www.amazon.com.br/s?k={q}&tag={amazon_tag}&linkCode=ll2&ref=as_li_ss_tl"
        elif "mercado" in s:
            ml_prog = db.query(AffiliateProgramModel).filter(AffiliateProgramModel.network_slug == "mercadolivre").first()
            ml_tag = ml_prog.tracking_id if (ml_prog and ml_prog.tracking_id) else "quepromo_ml"
            target_url = f"https://lista.mercadolivre.com.br/{q_slug}?matt_tool={ml_tag}"
        elif "magalu" in s or "magazine" in s:
            mag_prog = db.query(AffiliateProgramModel).filter(AffiliateProgramModel.network_slug == "magalu").first()
            mag_tag = mag_prog.tracking_id if (mag_prog and mag_prog.tracking_id) else "quepromo"
            target_url = f"https://www.magazineluiza.com.br/busca/{q_slug}/?parceiro={mag_tag}&tipo=link"
        elif "kabum" in s:
            target_url = f"https://www.kabum.com.br/busca/{q_slug}?tag=quepromo"
        elif "shopee" in s:
            target_url = f"https://shopee.com.br/search?keyword={q}&af_siteid=quepromo_sp"
        elif "casas" in s or "bahia" in s:
            target_url = f"https://www.casasbahia.com.br/{q_slug}/b?parceiro=quepromo"
        elif "terabyte" in s:
            target_url = f"https://www.terabyteshop.com.br/busca?str={q}"
        else:
            target_url = f"https://www.google.com/search?q={urllib.parse.quote_plus(clean_title + ' ' + (product.source or ''))}"
    else:
        # Se for uma URL direta da Amazon, injeta/substitui a tag do afiliado dinamicamente
        if "amazon.com.br" in target_url:
            import re
            if "tag=" in target_url:
                target_url = re.sub(r"tag=[^&]+", f"tag={amazon_tag}", target_url)
            else:
                sep = "&" if "?" in target_url else "?"
                target_url = f"{target_url}{sep}tag={amazon_tag}"

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
        "informatica": "Informática & Notebooks",
        "hardware": "Hardware & Peças PC",
        "perifericos": "Periféricos & Acessórios",
        "eletronicos": "Eletrônicos, Áudio & TV",
        "games": "Games & Consoles",
        "eletrodomesticos": "Eletrodomésticos & Cozinha",
        "casa": "Casa Inteligente & Decoração",
        "esportes": "Esportes & Calçados",
        "saude": "Saúde & Suplementos",
        "ferramentas": "Ferramentas & Jardim",
        "livros": "Livros & E-readers",
        "geral": "Geral & Outros"
    }
    return [
        {"slug": cat, "name": labels.get(cat, cat.replace("_", " ").title()), "total_deals": count}
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
        is_lightning_deal=deal_in.is_lightning_deal or 0,
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


@app.post("/api/admin/quick-import", response_model=DealOut)
def quick_import_deal(req: QuickImportRequest, db: Session = Depends(get_db)):
    """Importador expresso: analisa URL (Amazon ou qualquer loja), injeta tag de afiliado e cadastra direto."""
    now = datetime.utcnow()
    raw_url = req.url.strip()
    store = detect_store_from_url(raw_url).capitalize()
    store_slug = store.lower()

    extracted_title = ""
    asin = None
    extracted_image = req.image_url or ""

    if "amazon.com.br" in raw_url:
        store = "Amazon"
        store_slug = "amazon"
        asin_match = re.search(r"/(?:dp|gp/product|d)/([A-Z0-9]{10})", raw_url)
        if asin_match:
            asin = asin_match.group(1)
            if not extracted_image:
                extracted_image = f"https://m.media-amazon.com/images/P/{asin}.01._SCLZZZZZZZ_SX500_.jpg"

        slug_match = re.search(r"amazon\.com\.br/([^/?#]+)/dp/", raw_url)
        if slug_match:
            slug_raw = urllib.parse.unquote(slug_match.group(1)).replace("-", " ")
            if len(slug_raw) > 3 and not slug_raw.startswith("dp"):
                extracted_title = clean_title(slug_raw)

    title = req.custom_title or extracted_title or f"Super Oferta {store}"
    title = clean_title(title)
    cat = req.category or detect_category(title)
    brand = detect_brand(title)

    # Injeta a tag de afiliado configurada para a loja
    program = db.query(AffiliateProgramModel).filter(AffiliateProgramModel.network_slug == store_slug).first()
    custom_tag = program.tracking_id if program else ("thiagovinigo-20" if store_slug == "amazon" else None)
    affiliate_url = build_affiliate_url(raw_url, store_slug=store_slug, custom_tag=custom_tag)

    price = req.custom_price if (req.custom_price and req.custom_price > 0) else 99.0
    list_price = req.custom_list_price
    discount = calculate_discount_percent(price, list_price=list_price)
    if discount <= 0 and list_price and list_price > price:
        discount = round(((list_price - price) / list_price) * 100, 1)

    deal_id = f"quick_{asin or hashlib.md5(raw_url.encode('utf-8')).hexdigest()[:10]}"

    new_prod = ProductModel(
        id=deal_id,
        title=title,
        price=price,
        list_price=list_price,
        previous_price=list_price if (list_price and list_price > price) else None,
        lowest_historic_price=price,
        price_dropped=1 if (list_price and list_price > price) else 0,
        discount_percent=discount,
        brand=brand,
        category=cat,
        url=raw_url,
        affiliate_url=affiliate_url,
        source=store,
        image_url=extracted_image,
        is_available=1,
        coupon_code=req.coupon_code,
        free_shipping=1,
        is_affiliate_deal=1,
        is_featured=1 if req.is_featured else 0,
        is_lightning_deal=1 if req.is_lightning else 0,
        rating=4.9,
        review_count=85,
        clicks_count=0,
        created_at=now,
        last_updated=now,
        price_changed_at=now,
    )
    db.merge(new_prod)
    db.add(PriceHistoryModel(product_id=deal_id, price=price, seen_at=now))
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


# ==========================================
# AUTENTICAÇÃO DO PAINEL ADMINISTRATIVO
# ==========================================
ADMIN_MASTER_PASSWORD = os.getenv("ADMIN_PASSWORD", "!Thi5361206")


class AdminAuthRequest(BaseModel):
    password: str


@app.post("/api/admin/auth")
def admin_auth(req: AdminAuthRequest):
    """Valida a senha mestra para acesso seguro ao Painel Administrativo."""
    if req.password == ADMIN_MASTER_PASSWORD:
        return {
            "success": True,
            "authenticated": True,
            "token": hashlib.sha256(ADMIN_MASTER_PASSWORD.encode()).hexdigest(),
            "message": "Acesso concedido ao Painel Administrativo Só Promo Boa."
        }
    raise HTTPException(status_code=401, detail="Senha incorreta. Acesso negado ao painel administrativo.")



# ==========================================
# STORE HUNTER AI AGENT - ENDPOINTS
# ==========================================
class DiscoveredStoreOut(BaseModel):
    id: int
    slug: str
    name: str
    domain: str
    official_url: str
    logo_url: Optional[str] = None
    category: str
    reclame_aqui_score: Optional[float] = None
    reclame_aqui_badge: Optional[str] = None
    reclame_aqui_resolved_rate: Optional[float] = None
    trust_score: int
    affiliate_network: Optional[str] = None
    estimated_commission: Optional[str] = None
    affiliate_program_url: Optional[str] = None
    status: str
    discovered_reason: Optional[str] = None
    discovered_at: Optional[datetime] = None
    reviewed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class AuditUrlRequest(BaseModel):
    url: str
    store_name: Optional[str] = None


@app.get("/api/agent/hunter/stores", response_model=List[DiscoveredStoreOut])
def get_hunter_stores(
    status: str = Query("all", description="Filtrar por status: all, pending, approved, rejected"),
    category: Optional[str] = Query(None, description="Filtrar por categoria"),
    search: Optional[str] = Query(None, description="Buscar por nome ou domínio"),
    db: Session = Depends(get_db)
):
    """Lista lojas descobertas e auditadas pelo Store Hunter AI Agent."""
    query = db.query(DiscoveredStoreModel)
    if status and status != "all":
        query = query.filter(DiscoveredStoreModel.status == status)
    if category and category != "all":
        query = query.filter(DiscoveredStoreModel.category.ilike(f"%{category}%"))
    if search:
        query = query.filter(
            or_(
                DiscoveredStoreModel.name.ilike(f"%{search}%"),
                DiscoveredStoreModel.domain.ilike(f"%{search}%")
            )
        )
    return query.order_by(desc(DiscoveredStoreModel.trust_score), desc(DiscoveredStoreModel.id)).all()


@app.get("/api/agent/hunter/stats")
def get_hunter_stats(db: Session = Depends(get_db)):
    """Retorna métricas em tempo real do Store Hunter AI Agent."""
    total = db.query(DiscoveredStoreModel).count()
    pending = db.query(DiscoveredStoreModel).filter(DiscoveredStoreModel.status == "pending").count()
    approved = db.query(DiscoveredStoreModel).filter(DiscoveredStoreModel.status == "approved").count()
    rejected = db.query(DiscoveredStoreModel).filter(DiscoveredStoreModel.status == "rejected").count()
    avg_trust = db.query(func.avg(DiscoveredStoreModel.trust_score)).scalar() or 0
    avg_ra = db.query(func.avg(DiscoveredStoreModel.reclame_aqui_score)).scalar() or 0

    return {
        "total_discovered": total,
        "pending_approval": pending,
        "approved": approved,
        "rejected": rejected,
        "average_trust_score": round(float(avg_trust), 1),
        "average_reclame_aqui": round(float(avg_ra), 1),
    }


@app.post("/api/agent/hunter/run")
def run_hunter_cycle(db: Session = Depends(get_db)):
    """Aciona uma rodada de varredura e auditoria do Store Hunter AI Agent."""
    agent = StoreHunterAgent(db)
    result = agent.run_discovery_cycle()
    return result


@app.post("/api/agent/hunter/stores/{store_id}/approve")
def approve_hunter_store(store_id: int, db: Session = Depends(get_db)):
    """Aprova uma loja descoberta e a integra automaticamente ao catálogo do Só Promo Boa."""
    agent = StoreHunterAgent(db)
    result = agent.approve_store(store_id)
    if not result.get("success"):
        raise HTTPException(status_code=404, detail=result.get("message"))
    return result


@app.post("/api/agent/hunter/stores/{store_id}/reject")
def reject_hunter_store(store_id: int, db: Session = Depends(get_db)):
    """Descarta a sugestão de inclusão de uma loja."""
    agent = StoreHunterAgent(db)
    result = agent.reject_store(store_id)
    if not result.get("success"):
        raise HTTPException(status_code=404, detail=result.get("message"))
    return result


@app.post("/api/agent/hunter/audit")
def audit_custom_url(req: AuditUrlRequest, db: Session = Depends(get_db)):
    """Submete uma URL arbitrária de loja para auditoria instantânea do agente."""
    agent = StoreHunterAgent(db)
    return agent.audit_custom_url(req.url, req.store_name)

