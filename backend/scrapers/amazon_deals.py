"""Scraper de Ofertas da Amazon Brasil."""
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
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
}


def scrape_amazon() -> List[Dict[str, Any]]:
    """Raspagem da página de Ofertas e Promoções da Amazon Brasil."""
    url = "https://www.amazon.com.br/deals"
    results = []

    try:
        resp = requests.get(url, headers=HEADERS, timeout=12)
        if resp.status_code != 200:
            return results

        soup = BeautifulSoup(resp.text, "html.parser")
        cards = soup.select("[data-testid='deal-card'], .DealGridItem-module__dealItemContent_31R6e, [class*='DealCard']")

        for card in cards[:30]:
            title_el = card.select_one("[class*='dealTitle'], [class*='DealContent-module__truncate'], span.a-truncate-cut")
            if not title_el:
                continue
            title = title_el.get_text().strip()

            price_el = card.select_one(".a-price .a-offscreen, [class*='price']")
            if not price_el:
                continue
            price = extract_price(price_el.get_text())
            if price <= 0:
                continue

            # Preço riscado de lista
            list_price_el = card.select_one(".a-text-price .a-offscreen, [class*='basisPrice']")
            list_price = extract_price(list_price_el.get_text()) if list_price_el else None

            # Link
            link_el = card.select_one("a[href*='/dp/'], a[href*='/deal/'], a")
            if not link_el or not link_el.get("href"):
                continue
            href = link_el["href"]
            if not href.startswith("http"):
                product_url = f"https://www.amazon.com.br{href}".split("?")[0]
            else:
                product_url = href.split("?")[0]

            img_el = card.select_one("img[src]")
            image_url = img_el["src"] if img_el else ""

            item_id = f"amz_{hashlib.md5(product_url.encode('utf-8')).hexdigest()[:12]}"

            results.append({
                "id": item_id,
                "title": title,
                "price": price,
                "list_price": list_price,
                "url": product_url,
                "source": "Amazon",
                "image_url": image_url,
                "free_shipping": 1 if "prime" in card.get_text().lower() else 0,
            })

    except Exception as e:
        print(f"[Scraper Amazon] Erro durante a raspagem: {e}")

    return results
