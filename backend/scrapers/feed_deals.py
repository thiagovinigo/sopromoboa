"""Scraper / Agregador de Feeds RSS e Canais Abertos de Promoções."""
import hashlib
import requests
import xml.etree.ElementTree as ET
from typing import List, Dict, Any
from scrapers.price_utils import extract_price

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; SoPromoBoaBot/1.0; +https://sopromoboa.com.br)",
    "Accept": "application/rss+xml, application/xml, text/xml, */*",
}


def scrape_rss_feed() -> List[Dict[str, Any]]:
    """Lê feeds RSS de canais públicos de promoções e ofertas da internet brasileira."""
    results = []
    # Feed demonstrativo de ofertas / RSS agregador
    feed_urls = [
        "https://www.promobit.com.br/feed/promocoes/",
    ]

    for feed_url in feed_urls:
        try:
            resp = requests.get(feed_url, headers=HEADERS, timeout=8)
            if resp.status_code != 200:
                continue

            root = ET.fromstring(resp.content)
            channel = root.find("channel")
            if not channel:
                continue

            for item in channel.findall("item")[:20]:
                title_el = item.find("title")
                link_el = item.find("link")
                desc_el = item.find("description")

                if title_el is None or link_el is None:
                    continue

                raw_title = title_el.text or ""
                link = link_el.text or ""
                desc = desc_el.text if desc_el is not None else ""

                price = extract_price(raw_title) or extract_price(desc)
                if price <= 0:
                    continue

                item_id = f"feed_{hashlib.md5(link.encode('utf-8')).hexdigest()[:12]}"

                results.append({
                    "id": item_id,
                    "title": raw_title,
                    "price": price,
                    "url": link,
                    "source": "Promobit",
                    "image_url": "",
                })
        except Exception as e:
            # Feeds externos podem oscilar sem quebrar a execução geral do worker
            print(f"[Scraper RSS] Erro ao ler {feed_url}: {e}")

    return results
