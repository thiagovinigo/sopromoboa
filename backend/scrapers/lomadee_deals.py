"""Scraper do catálogo da Lomadee via API oficial: produtos reais de lojas parceiras com comissão.

Só roda com LOMADEE_API_KEY configurada. Os preços de lista são os informados pela própria loja,
então estes itens entram sem histórico: quedas só serão apontadas depois de novas varreduras.
"""
import os
from typing import Any, Dict, List

from lomadee_client import (
    collect_listings,
    fetch_brands,
    get_api_key,
    index_brands,
    iter_products,
    select_listings,
)

MAX_PAGES = int(os.getenv("LOMADEE_MAX_PAGES", "600"))
PER_BRAND_CAP = int(os.getenv("LOMADEE_PER_BRAND_CAP", "2000"))
TOTAL_CAP = int(os.getenv("LOMADEE_TOTAL_CAP", "12000"))


def scrape_lomadee() -> List[Dict[str, Any]]:
    api_key = get_api_key()
    if not api_key:
        print("[Scraper Lomadee] LOMADEE_API_KEY ausente; nada a coletar.")
        return []

    try:
        brands = index_brands(fetch_brands(api_key))
        listings = collect_listings(brands, iter_products(api_key, MAX_PAGES))
    except Exception as err:
        print(f"[Scraper Lomadee] Erro na coleta: {err}")
        return []

    selected = select_listings(listings, per_brand_cap=PER_BRAND_CAP, total_cap=TOTAL_CAP)
    print(f"[Scraper Lomadee] {len(selected)} ofertas selecionadas de {len(listings)} aproveitáveis.")
    return selected
