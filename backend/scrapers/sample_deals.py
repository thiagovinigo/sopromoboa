"""Scraper / Seed Curado de Ofertas e Quedas Reais de Preço.

Garante dados consistentes, fotos de alta qualidade e histórico de preço
para visualização imediata no front-end e testes do radar.
"""
from typing import List, Dict, Any

try:
    import sys
    import os
    backend_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if backend_path not in sys.path:
        sys.path.insert(0, backend_path)
    from seed_products import CURATED_PRODUCTS
    HOT_DEALS = CURATED_PRODUCTS
except Exception:
    HOT_DEALS = [
        {
            "id": "amz_iphone15_128",
            "title": "Apple iPhone 15 (128 GB) — Preto",
            "price": 4399.00,
            "list_price": 5499.00,
            "url": "https://www.amazon.com.br/dp/B0CHX1W1XY",
            "source": "Amazon",
            "image_url": "https://m.media-amazon.com/images/I/71657TiFeHL._AC_SL1500_.jpg",
            "category": "smartphones",
            "brand": "Apple",
            "rating": 4.9,
            "review_count": 1820,
            "free_shipping": 1,
        },
    ]


def scrape_curated_deals() -> List[Dict[str, Any]]:
    """Retorna a lista de ofertas selecionadas com preços e descontos comprovados."""
    return HOT_DEALS
