"""Scraper do feed de afiliados da Shopee: ofertas com link de afiliado oficial vindo do próprio feed.

Só roda com SHOPEE_FEED_URLS configurada. Preço de lista e preço promocional são os informados pela loja,
então os itens entram sem histórico: quedas só serão apontadas depois de novas varreduras.
"""
import os
from typing import Any, Dict, List

from lomadee_client import select_listings
from shopee_feed import feed_sources, read_feed_listings

PER_CATEGORY_CAP = int(os.getenv("SHOPEE_FEED_PER_CATEGORY_CAP", "1500"))
TOTAL_CAP = int(os.getenv("SHOPEE_FEED_TOTAL_CAP", "5000"))


def scrape_shopee_feed() -> List[Dict[str, Any]]:
    sources = feed_sources()
    if not sources:
        print("[Scraper Shopee Feed] SHOPEE_FEED_URLS ausente; nada a coletar.")
        return []

    unique: Dict[str, Dict[str, Any]] = {}
    for source in sources:
        try:
            for listing in read_feed_listings(source):  # em fluxo: só os itens bons ficam na memória
                unique.setdefault(listing["id"], listing)
        except Exception as err:
            print(f"[Scraper Shopee Feed] Erro ao ler um feed: {type(err).__name__}")
    listings = list(unique.values())

    selected = select_listings(listings, per_brand_cap=PER_CATEGORY_CAP, total_cap=TOTAL_CAP, group_key="category")
    print(f"[Scraper Shopee Feed] {len(selected)} ofertas selecionadas de {len(listings)} aproveitáveis.")
    return selected
