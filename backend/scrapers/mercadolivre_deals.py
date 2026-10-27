"""Scraper do Mercado Livre via API oficial: produtos de catálogo mais vendidos, com preço real de oferta.

Só roda com ML_APP_ID e ML_APP_SECRET configurados. O link vai direto para a página do anúncio e a tag de
afiliado (matt_tool) entra em normalize/affiliate. O preço de lista só existe quando o próprio vendedor o
informa (original_price); sem ele o item entra sem desconto, e nunca com preço de lista inventado.
"""
import concurrent.futures
import os
from typing import Any, Dict, List

from mercadolivre_client import (
    MercadoLivreClient,
    collect_product_refs,
    fetch_listing,
    get_credentials,
    iter_highlights,
    limit_refs,
)

MAX_PRODUCTS = int(os.getenv("ML_MAX_PRODUCTS", "3000"))
FETCH_WORKERS = int(os.getenv("ML_FETCH_WORKERS", "4"))


def scrape_mercadolivre() -> List[Dict[str, Any]]:
    credentials = get_credentials()
    if not credentials:
        print("[Scraper Mercado Livre] ML_APP_ID/ML_APP_SECRET ausentes; nada a coletar.")
        return []

    try:
        client = MercadoLivreClient(*credentials)
        refs = limit_refs(collect_product_refs(iter_highlights(client)), MAX_PRODUCTS)
    except Exception as err:
        print(f"[Scraper Mercado Livre] Erro ao listar destaques: {err}")
        return []

    def fetch(ref):
        product_id, category_name = ref
        try:
            return fetch_listing(client, product_id, category_name)
        except Exception as err:
            print(f"[Scraper Mercado Livre] Falha em {product_id}: {err}")
            return None

    with concurrent.futures.ThreadPoolExecutor(max_workers=FETCH_WORKERS) as pool:
        listings = [listing for listing in pool.map(fetch, refs) if listing]

    print(f"[Scraper Mercado Livre] {len(listings)} ofertas aproveitadas de {len(refs)} produtos.")
    return listings
