"""Scraper do Gatry (agregador aberto de ofertas da comunidade): ofertas recentes da Amazon, Mercado Livre,
Magazine Luiza e outras lojas, com link direto do produto (a tag do Gatry é removida; a nossa entra depois).

O Gatry mostra só o preço atual: não há preço de lista nem histórico, então os itens entram sem desconto
declarado. A idade vem do carimbo de data da oferta (horário de Brasília) e ofertas velhas são descartadas.
"""
import hashlib
import os
import re
import time
from datetime import datetime, timedelta
from typing import Any, Callable, Dict, List, Optional
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup, Tag

from scrapers.price_utils import extract_price

MAX_PAGES = int(os.getenv("GATRY_MAX_PAGES", "60"))
MAX_AGE_HOURS = int(os.getenv("GATRY_MAX_AGE_HOURS", "96"))
PAGE_DELAY_SECONDS = 0.6
REQUEST_TIMEOUT_SECONDS = 15
BRAZIL_UTC_OFFSET_HOURS = 3
LISTING_URL = "https://gatry.com/?page={page}"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
}

_UNTAGGABLE_HOSTS = ("meli.la", "link.amazon", "amzn.to", "amzn.com", "a.co")
_REQUIRED_DOMAINS = {"Amazon": "amazon.com.br", "Mercado Livre": "mercadolivre.com.br"}
_DATE_RE = re.compile(r"(\d{2})/(\d{2})/(\d{4})\D+(\d{2}):(\d{2})")
_STORE_ALIASES = [
    ("amazon", "Amazon"),
    ("magalu", "Magazine Luiza"),
    ("magazine", "Magazine Luiza"),
    ("mercado", "Mercado Livre"),
    ("meli", "Mercado Livre"),
    ("kabum", "KaBuM!"),
    ("shopee", "Shopee"),
]


def store_name(label: str) -> str:
    text = (label or "").replace("Ir para", "").strip()
    lowered = text.lower()
    for needle, name in _STORE_ALIASES:
        if needle in lowered:
            return name
    return text.title() or "Online"


def parse_posted_at(card: Tag) -> Optional[datetime]:
    """Data da oferta em UTC. O cartão tem mais de um carimbo (o do bloco mobile às vezes vem errado): vale o mais recente."""
    moments: List[datetime] = []
    for node in card.select("p.date"):
        match = _DATE_RE.search(node.get("title", ""))
        if not match:
            continue
        day, month, year, hour, minute = (int(part) for part in match.groups())
        try:
            local = datetime(year, month, day, hour, minute)
        except ValueError:
            continue
        moments.append(local + timedelta(hours=BRAZIL_UTC_OFFSET_HOURS))
    return max(moments) if moments else None


def is_fresh(posted_at: Optional[datetime], now: datetime, max_age_hours: int) -> bool:
    if posted_at is None:
        return False
    age = now - posted_at
    return timedelta(hours=-1) <= age <= timedelta(hours=max_age_hours)


def is_taggable_url(source: str, url: str) -> bool:
    """Só vale link que podemos marcar com a nossa tag. Links curtos (meli.la, link.amazon, amzn.to) carregam o
    afiliado de quem os criou e mandariam a comissão para outra pessoa; Amazon e Mercado Livre exigem o domínio oficial."""
    host = (urlparse(url).hostname or "").lower()
    if not host or any(host == bad or host.endswith("." + bad) for bad in _UNTAGGABLE_HOSTS):
        return False
    required_domain = _REQUIRED_DOMAINS.get(source)
    return required_domain is None or host == required_domain or host.endswith("." + required_domain)


def card_to_raw(card: Tag) -> Optional[Dict[str, Any]]:
    title_el = card.select_one("h3 a")
    price_el = card.select_one(".price")
    if not title_el or not price_el or not title_el.get("href"):
        return None

    title = title_el.get_text().strip()
    price = extract_price(price_el.get_text())
    if not title or price <= 0:
        return None

    clean_url = title_el["href"].split("?")[0]
    store_el = card.select_one(".option-store a")
    if not is_taggable_url(store_name(store_el.get_text() if store_el else ""), clean_url):
        return None
    image_el = card.select_one(".image img")
    image_url = ""
    if image_el:
        image_url = image_el.get("src") or image_el.get("data-src") or ""
        if image_url.startswith("//"):
            image_url = "https:" + image_url
        elif image_url.startswith("/"):
            image_url = "https://gatry.com" + image_url

    coupon_code = None
    coupon_el = card.select_one(".coupon, .cupom, [class*='coupon']")
    if coupon_el:
        text = coupon_el.get_text().strip()
        if text and len(text) < 30 and not text.startswith("R$"):
            coupon_code = text.replace("Cupom:", "").replace("CUPOM:", "").strip()

    return {
        "id": f"gatry_{hashlib.md5(clean_url.encode('utf-8')).hexdigest()[:12]}",
        "title": title,
        "price": price,
        "url": clean_url,
        "source": store_name(store_el.get_text() if store_el else ""),
        "image_url": image_url,
        "coupon_code": coupon_code,
        "free_shipping": 0,
    }


def collect_fresh_deals(
    fetch_cards: Callable[[int], List[Tag]], now: datetime, max_pages: int, max_age_hours: int
) -> List[Dict[str, Any]]:
    """Percorre as páginas (da mais nova para a mais velha) e para na primeira sem nenhuma oferta recente."""
    deals: Dict[str, Dict[str, Any]] = {}
    for page in range(1, max_pages + 1):
        found_fresh = False
        for card in fetch_cards(page):
            if not is_fresh(parse_posted_at(card), now, max_age_hours):
                continue
            found_fresh = True
            raw = card_to_raw(card)
            if raw:
                deals.setdefault(raw["id"], raw)
        if not found_fresh:
            break
    return list(deals.values())


def _fetch_cards(session: requests.Session, page: int) -> List[Tag]:
    try:
        resp = session.get(LISTING_URL.format(page=page), headers=HEADERS, timeout=REQUEST_TIMEOUT_SECONDS)
        if resp.status_code != 200:
            return []
        time.sleep(PAGE_DELAY_SECONDS)
        return BeautifulSoup(resp.text, "html.parser").select("article")
    except requests.RequestException as err:
        print(f"[Scraper Gatry] Erro na página {page}: {err}")
        return []


def scrape_gatry() -> List[Dict[str, Any]]:
    """Ofertas recentes do Gatry (até GATRY_MAX_PAGES páginas, só as dos últimos GATRY_MAX_AGE_HOURS horas)."""
    with requests.Session() as session:
        deals = collect_fresh_deals(
            lambda page: _fetch_cards(session, page), datetime.utcnow(), MAX_PAGES, MAX_AGE_HOURS
        )
    print(f"[Scraper Gatry] {len(deals)} ofertas recentes coletadas.")
    return deals
