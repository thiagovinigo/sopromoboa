"""Worker de Scraping Concorrente e Detecção de Queda de Preços do Só Promo Boa.

- Descobre dinamicamente os scrapers na pasta 'scrapers/'
- Executa raspagens concorrentes via ThreadPoolExecutor
- Normaliza títulos, marcas e categorias
- Audita preços: calcula descontos, detecta quedas reais e grava histórico
- Aplica tags do sistema de afiliados
- Dispara alertas salvos pelos usuários
"""
import os
import sys
import time
import importlib
import inspect
import datetime
import concurrent.futures
from typing import List, Dict, Any

from sqlalchemy import func, or_

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from database import SessionLocal, engine, Base
from models import ProductModel, PriceHistoryModel, StoreModel, AlertModel, AffiliateProgramModel
from normalize import normalize_listing
from pricing import apply_price_change, is_price_drop_active, calculate_discount_percent
from affiliate import build_affiliate_url
from feature_flags import LIGHTNING_ENABLED
from lomadee_client import PRODUCT_ID_PREFIX as LOMADEE_ID_PREFIX, is_short_link
from shopee_feed import PRODUCT_ID_PREFIX as SHOPEE_FEED_ID_PREFIX

# Scrapers de catálogo completo: o item que some do catálogo sai do ar. Valor = prefixo de id do scraper.
GATRY_ID_PREFIX = "gatry_"
RETIRING_SCRAPERS = {"Lomadee": LOMADEE_ID_PREFIX, "Shopee Feed": SHOPEE_FEED_ID_PREFIX, "Gatry": GATRY_ID_PREFIX}
# Itens desses scrapers chegam sem histórico de preço: não ganham "menor preço" no primeiro registro.
NO_HISTORY_PREFIXES = (LOMADEE_ID_PREFIX, SHOPEE_FEED_ID_PREFIX, GATRY_ID_PREFIX)
# Varredura quase vazia = provável falha parcial da fonte: não retira o catálogo inteiro por causa dela.
MIN_ITEMS_TO_RETIRE = 20

# Garante a criação de todas as tabelas
Base.metadata.create_all(bind=engine)


def discover_scrapers() -> List[Dict[str, Any]]:
    """Descobre dinamicamente todas as funções 'scrape_*' dentro da pasta scrapers/."""
    scrapers = []
    scrapers_dir = os.path.join(os.path.dirname(__file__), "scrapers")

    if not os.path.isdir(scrapers_dir):
        return scrapers

    for filename in os.listdir(scrapers_dir):
        if filename.endswith(".py") and not filename.startswith("__"):
            module_name = f"scrapers.{filename[:-3]}"
            try:
                module = importlib.import_module(module_name)
                for name, obj in inspect.getmembers(module, inspect.isfunction):
                    if name.startswith("scrape_"):
                        store_name = name.replace("scrape_", "").replace("_", " ").title()
                        scrapers.append({
                            "name": store_name,
                            "func": obj,
                            "module": filename
                        })
            except Exception as e:
                print(f"[Worker] Erro ao carregar scraper de {filename}: {e}")

    return scrapers


# Fontes descontinuadas e links que pagam comissão a terceiros saem do catálogo a cada ciclo.
DISCONTINUED_ID_PREFIXES = ("ml_",)
THIRD_PARTY_LINK_MARKERS = ("meli.la", "link.amazon", "amzn.to", "amzn.com")


def retire_discontinued_items(db) -> int:
    conditions = [ProductModel.id.startswith(prefix, autoescape=True) for prefix in DISCONTINUED_ID_PREFIXES]
    for marker in THIRD_PARTY_LINK_MARKERS:
        conditions.append(ProductModel.url.contains(marker, autoescape=True))
        conditions.append(ProductModel.affiliate_url.contains(marker, autoescape=True))

    retired = db.query(ProductModel).filter(ProductModel.is_available == 1, or_(*conditions)).update(
        {"is_available": 0}, synchronize_session=False
    )
    db.commit()
    return retired


def clear_unproven_lowest_prices(db) -> int:
    """Itens de catálogo com um único registro de preço não têm 'menor preço histórico' a afirmar.

    Corrige linhas gravadas antes da regra (o primeiro preço era gravado como menor preço). Itens com mais de
    um ponto de preço, ou seja, com variação realmente observada, mantêm o valor.
    """
    price_points = (
        db.query(PriceHistoryModel.product_id)
        .group_by(PriceHistoryModel.product_id)
        .having(func.count(PriceHistoryModel.id) > 1)
    )
    catalog_ids = [ProductModel.id.startswith(prefix, autoescape=True) for prefix in NO_HISTORY_PREFIXES]
    cleared = (
        db.query(ProductModel)
        .filter(
            or_(*catalog_ids),
            ProductModel.lowest_historic_price.isnot(None),
            ~ProductModel.id.in_(price_points),
        )
        .update({"lowest_historic_price": None}, synchronize_session=False)
    )
    db.commit()
    return cleared


def retire_missing_products(db, store_info: Dict[str, Any], seen_ids: List[str]) -> int:
    """Marca como indisponíveis os itens de um scraper de catálogo que sumiram na última varredura."""
    prefix = RETIRING_SCRAPERS.get(store_info["name"])
    if not prefix or len(seen_ids) < MIN_ITEMS_TO_RETIRE:
        return 0

    seen = set(seen_ids)
    rows = db.query(ProductModel.id).filter(
        ProductModel.id.startswith(prefix, autoescape=True),
        ProductModel.is_available == 1,
    ).all()
    stale = [product_id for (product_id,) in rows if product_id not in seen]
    for start in range(0, len(stale), 500):
        db.query(ProductModel).filter(ProductModel.id.in_(stale[start:start + 500])).update(
            {"is_available": 0}, synchronize_session=False
        )
    return len(stale)


def process_scraped_items(store_info: Dict[str, Any], raw_items: List[Dict[str, Any]]) -> Dict[str, int]:
    """Processa e persiste em lote as ofertas raspadas de uma loja com isolamento de transação."""
    db = SessionLocal()
    stats = {"inserted": 0, "updated": 0, "price_drops": 0, "alerts_triggered": 0}

    try:
        now = datetime.datetime.utcnow()
        scraped_ids = []

        # Carrega programas de afiliados ativos para injeção rápida de tags
        affiliate_programs = {p.network_slug: p.tracking_id for p in db.query(AffiliateProgramModel).filter(AffiliateProgramModel.status == "active").all()}

        # Carrega alertas de usuários ativos
        active_alerts = db.query(AlertModel).filter(AlertModel.is_active == 1).all()

        for raw in raw_items:
            try:
                item = normalize_listing(raw)
            except Exception as e:
                print(f"[Worker] Erro na normalização de {raw.get('title')}: {e}")
                continue

            product_id = item["id"]
            scraped_ids.append(product_id)

            # Injeta tag de afiliado se houver programa cadastrado
            store_slug = item["source"].lower()
            # Link de afiliado trazido pelo próprio scraper (ex.: feed da Shopee) tem prioridade sobre a tag genérica
            if store_slug in affiliate_programs and not raw.get("affiliate_url"):
                item["affiliate_url"] = build_affiliate_url(
                    item["url"],
                    store_slug=store_slug,
                    custom_tag=affiliate_programs[store_slug]
                )

            db_prod = db.query(ProductModel).filter(ProductModel.id == product_id).first()

            if db_prod:
                # Produto existente: avalia oscilação de preço
                price_changes = apply_price_change(
                    old_price=db_prod.price,
                    new_price=item["price"],
                    now=now,
                    historic_lowest=db_prod.lowest_historic_price
                )

                if "previous_price" in price_changes and price_changes["previous_price"]:
                    stats["price_drops"] += 1

                for col, val in price_changes.items():
                    setattr(db_prod, col, val)

                # Se o preço mudou, registra novo ponto no gráfico de histórico
                if "price" in price_changes:
                    db.add(PriceHistoryModel(
                        product_id=product_id,
                        price=price_changes["price"],
                        seen_at=now
                    ))

                # Atualiza flag de queda ativa
                db_prod.price_dropped = int(is_price_drop_active(
                    db_prod.price,
                    db_prod.previous_price,
                    db_prod.price_changed_at,
                    now
                ))

                # Recalcula percentual de desconto real
                db_prod.discount_percent = calculate_discount_percent(
                    db_prod.price,
                    list_price=item.get("list_price") or db_prod.list_price,
                    previous_price=db_prod.previous_price
                )
                if LIGHTNING_ENABLED and db_prod.discount_percent >= 25.0:
                    db_prod.is_lightning_deal = 1

                # Atualiza metadados
                db_prod.title = item["title"]
                db_prod.list_price = item.get("list_price")
                db_prod.category = item["category"]
                db_prod.brand = item.get("brand") or db_prod.brand
                db_prod.image_url = item.get("image_url") or db_prod.image_url
                if not is_short_link(db_prod.affiliate_url):  # preserva o link comissionado já gerado
                    db_prod.affiliate_url = item["affiliate_url"]
                db_prod.coupon_code = item.get("coupon_code") or db_prod.coupon_code
                db_prod.free_shipping = item.get("free_shipping", 0)
                db_prod.is_available = 1
                db_prod.last_updated = now

                stats["updated"] += 1
            else:
                # Novo produto descoberto
                is_lightning = 1 if LIGHTNING_ENABLED and item["discount_percent"] >= 25.0 else 0
                # Itens de catálogo chegam sem histórico: sem "menor preço" até haver variação real observada
                first_lowest_price = None if product_id.startswith(NO_HISTORY_PREFIXES) else item["price"]
                new_prod = ProductModel(
                    id=product_id,
                    title=item["title"],
                    price=item["price"],
                    list_price=item.get("list_price"),
                    previous_price=None,
                    lowest_historic_price=first_lowest_price,
                    price_dropped=0,
                    discount_percent=item["discount_percent"],
                    brand=item.get("brand"),
                    category=item["category"],
                    subcategory=item.get("subcategory"),
                    url=item["url"],
                    affiliate_url=item["affiliate_url"],
                    source=item["source"],
                    image_url=item.get("image_url"),
                    is_available=1,
                    rating=item.get("rating"),
                    review_count=item.get("review_count", 0),
                    coupon_code=item.get("coupon_code"),
                    free_shipping=item.get("free_shipping", 0),
                    is_lightning_deal=is_lightning,
                    created_at=now,
                    last_updated=now,
                    price_changed_at=now,
                )
                db.add(new_prod)
                db.add(PriceHistoryModel(product_id=product_id, price=item["price"], seen_at=now))
                stats["inserted"] += 1

                # Avalia alertas de usuários para a nova oferta
                for alert in active_alerts:
                    if alert.search_term.lower() in item["title"].lower():
                        price_ok = (alert.target_price is None or item["price"] <= alert.target_price)
                        discount_ok = (alert.min_discount_percent is None or item["discount_percent"] >= alert.min_discount_percent)
                        if price_ok and discount_ok:
                            alert.matched_count = (alert.matched_count or 0) + 1
                            alert.last_notified_at = now
                            stats["alerts_triggered"] += 1
                            print(f"[ALERTA DISPARADO] Oferta '{item['title']}' atingiu R$ {item['price']} (Desconto: {item['discount_percent']}%)!")

        retired = retire_missing_products(db, store_info, scraped_ids)
        if retired:
            print(f"[Worker] {retired} itens de {store_info['name']} marcados como indisponíveis.")
        db.flush()

        # Atualiza métricas de cada loja do lote (a Lomadee entrega várias lojas de uma vez)
        source_names = {raw.get("source", store_info["name"]) for raw in raw_items} or {store_info["name"]}
        for source_name in sorted(source_names):
            store_entry = db.query(StoreModel).filter(StoreModel.name == source_name).first()
            if not store_entry:
                slug = source_name.lower().replace(" ", "_")
                store_entry = StoreModel(slug=slug, name=source_name, is_active=1)
                db.add(store_entry)

            store_entry.total_deals = db.query(ProductModel).filter(ProductModel.source == source_name, ProductModel.is_available == 1).count()

        db.commit()
    except Exception as e:
        db.rollback()
        print(f"[Worker] Erro ao sincronizar itens da loja {store_info['name']}: {e}")
    finally:
        db.close()

    return stats


def run_worker_once() -> Dict[str, Any]:
    """Executa uma rodada completa de scrapers concorrentes."""
    scrapers = discover_scrapers()
    print("\n=======================================================")
    print(f"[SO PROMO BOA WORKER] Iniciando varredura com {len(scrapers)} scrapers ativos...")
    print("=======================================================")

    cleanup_db = SessionLocal()
    try:
        retired = retire_discontinued_items(cleanup_db)
        if retired:
            print(f"[Worker] {retired} itens de fontes descontinuadas ou com link de terceiros foram retirados.")
        cleared = clear_unproven_lowest_prices(cleanup_db)
        if cleared:
            print(f"[Worker] 'menor preço' sem histórico removido de {cleared} itens.")
    finally:
        cleanup_db.close()

    start_time = time.time()
    total_stats = {"inserted": 0, "updated": 0, "price_drops": 0, "alerts_triggered": 0}

    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        future_to_scraper = {
            executor.submit(scraper["func"]): scraper for scraper in scrapers
        }

        for future in concurrent.futures.as_completed(future_to_scraper):
            scraper = future_to_scraper[future]
            try:
                data = future.result()
                if data:
                    print(f"[OK] [{scraper['name']}] {len(data)} ofertas encontradas. Sincronizando com o banco...")
                    stats = process_scraped_items(scraper, data)
                    for k in total_stats:
                        total_stats[k] += stats.get(k, 0)
                else:
                    print(f"[INFO] [{scraper['name']}] Nenhuma oferta retornada nesta iteração.")
            except Exception as exc:
                print(f"[ERRO] [{scraper['name']}] Falha ao executar: {exc}")

    elapsed = round(time.time() - start_time, 2)
    print(f"\n[WORKER CONCLUIDO em {elapsed}s]")
    print(f"Novas ofertas: {total_stats['inserted']} | Atualizadas: {total_stats['updated']} | Quedas de preco: {total_stats['price_drops']} | Alertas: {total_stats['alerts_triggered']}\n")

    return total_stats


if __name__ == "__main__":
    loop = "--loop" in sys.argv
    interval = 3600 # 1 hora padrão

    if loop:
        print(f"Iniciando worker em loop contínuo (intervalo de {interval}s)...")
        while True:
            run_worker_once()
            time.sleep(interval)
    else:
        run_worker_once()
