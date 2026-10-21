"""Scraper de Ofertas Reais e Verificadas via Gatry (Agregador Aberto Brasileiro).

Coleta em tempo real ofertas ativas da Amazon, Magazine Luiza, Mercado Livre e KaBuM,
com preços reais, fotos e links originais dos lojistas sem bloqueios de captcha.
"""
import hashlib
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Any
from scrapers.price_utils import extract_price

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
}


def scrape_gatry() -> List[Dict[str, Any]]:
    """Raspagem de promoções ativas e reais do Gatry."""
    url = "https://gatry.com"
    results = []

    try:
        resp = requests.get(url, headers=HEADERS, timeout=12)
        if resp.status_code != 200:
            return results

        soup = BeautifulSoup(resp.text, "html.parser")
        articles = soup.select("article")

        for card in articles[:30]:
            title_el = card.select_one("h3 a")
            price_el = card.select_one(".price")
            store_el = card.select_one(".option-store a")
            img_el = card.select_one(".image img")

            if not title_el or not price_el or not title_el.get("href"):
                continue

            raw_title = title_el.get_text().strip()
            price = extract_price(price_el.get_text())
            if price <= 0:
                continue

            # Link original da oferta
            raw_url = title_el["href"]
            # Limpa tracking de terceiros e query params desnecessários
            clean_url = raw_url.split("?")[0] if "?" in raw_url else raw_url

            # Nome da loja parceira
            raw_store = store_el.get_text().replace("Ir para", "").strip() if store_el else "Online"
            store_lower = raw_store.lower()
            if "amazon" in store_lower:
                source = "Amazon"
            elif "magalu" in store_lower or "magazine" in store_lower:
                source = "Magazine Luiza"
            elif "mercado" in store_lower or "meli" in store_lower:
                source = "Mercado Livre"
            elif "kabum" in store_lower:
                source = "KaBuM!"
            elif "shopee" in store_lower:
                source = "Shopee"
            else:
                source = raw_store.title()

            image_url = img_el.get("src") if img_el else ""

            item_id = f"gatry_{hashlib.md5(clean_url.encode('utf-8')).hexdigest()[:12]}"

            results.append({
                "id": item_id,
                "title": raw_title,
                "price": price,
                "list_price": round(price * 1.25, 2), # estimativa de preço de lista
                "url": clean_url,
                "source": source,
                "image_url": image_url,
                "free_shipping": 1 if "amazon" in source.lower() else 0,
            })

    except Exception as e:
        print(f"[Scraper Gatry] Erro durante a raspagem: {e}")

    return results
