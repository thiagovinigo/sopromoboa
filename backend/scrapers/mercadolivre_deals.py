"""Scraper de Ofertas do Dia do Mercado Livre Brasil."""
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
    "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
}


def scrape_mercadolivre() -> List[Dict[str, Any]]:
    """Raspagem da página de Ofertas do Mercado Livre Brasil."""
    url = "https://www.mercadolivre.com.br/ofertas"
    results = []

    try:
        resp = requests.get(url, headers=HEADERS, timeout=12)
        if resp.status_code != 200:
            return results

        soup = BeautifulSoup(resp.text, "html.parser")
        cards = soup.select(".promotion-item, .poly-card, .ui-search-result__wrapper, [class*='promotion-item']")

        for card in cards[:30]:
            title_el = card.select_one(".promotion-item__title, .poly-component__title, [class*='title']")
            if not title_el:
                continue
            title = title_el.get_text().strip()

            # Preço atual
            price_el = card.select_one(
                ".andes-money-amount--cents-superscript .andes-money-amount__fraction, "
                ".promotion-item__price span, "
                ".poly-price__current .andes-money-amount__fraction"
            )
            cents_el = card.select_one(".andes-money-amount__cents")
            if not price_el:
                continue

            raw_price = price_el.get_text().replace(".", "").strip()
            cents = cents_el.get_text().strip() if cents_el else "00"
            try:
                price = float(f"{raw_price}.{cents}")
            except ValueError:
                continue

            if price <= 0:
                continue

            # Preço de lista (original antes do desconto)
            list_price = None
            old_price_el = card.select_one(
                ".andes-money-amount--previous .andes-money-amount__fraction, "
                ".promotion-item__old-price"
            )
            if old_price_el:
                list_price = extract_price(old_price_el.get_text())

            # Link do produto
            link_el = card.select_one("a[href*='mercadolivre.com.br'], a.promotion-item__link-container, a.poly-component__title")
            if not link_el or not link_el.get("href"):
                continue
            product_url = link_el["href"].split("?")[0] # limpa query parameters para URL canônica

            # Imagem
            img_el = card.select_one("img[src], img[data-src]")
            image_url = ""
            if img_el:
                image_url = img_el.get("data-src") or img_el.get("src") or ""

            # ID estável
            item_id = f"ml_{hashlib.md5(product_url.encode('utf-8')).hexdigest()[:12]}"

            # Frete grátis
            free_shipping = 1 if card.select_one("[class*='shipping--free'], [class*='shipping-tag']") else 0

            results.append({
                "id": item_id,
                "title": title,
                "price": price,
                "list_price": list_price,
                "url": product_url,
                "source": "Mercado Livre",
                "image_url": image_url,
                "free_shipping": free_shipping,
            })

    except Exception as e:
        print(f"[Scraper Mercado Livre] Erro durante a raspagem: {e}")

    return results
