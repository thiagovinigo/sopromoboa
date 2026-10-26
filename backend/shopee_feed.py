"""Feed de produtos de afiliados da Shopee (CSV diário): leitura, filtros de qualidade e conversão.

O feed "Shopee Brasil" traz o link direto do produto e o link curto de afiliado já gerado, então os itens
entram com o link oficial. O endereço do feed (parâmetro id) funciona como credencial de download e vem da
variável SHOPEE_FEED_URLS (backend/.env, fora do git).
"""
import csv
import io
import os
import re
from typing import Any, Dict, Iterable, Iterator, List, Optional

import requests
from dotenv import load_dotenv

from category_map import category_for
from content_policy import is_restricted_listing

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))

PRODUCT_ID_PREFIX = "shf_"
SOURCE_NAME = "Shopee"
DOWNLOAD_TIMEOUT_SECONDS = (15, 180)  # (conexão, leitura): o arquivo tem ~20 MB

MIN_PRICE = 10.0
MAX_PRICE = 20_000.0
MIN_DISCOUNT_PERCENT = 10.0
MAX_DISCOUNT_PERCENT = 70.0
MIN_RATING = 4.0

_PRODUCT_LINK_RE = re.compile(r"^https://shopee\.com\.br/product/\d+/\d+$")
_SHORT_LINK_PREFIX = "https://shope.ee/"

csv.field_size_limit(50_000_000)  # descrições do feed podem ser longas


def feed_sources() -> List[str]:
    raw = os.getenv("SHOPEE_FEED_URLS", "")
    return [item.strip() for item in raw.split(",") if item.strip()]


def read_feed_text(source: str) -> str:
    """Lê o CSV de uma URL https ou de um arquivo local (útil em testes)."""
    if source.startswith("https://"):
        resp = requests.get(source, timeout=DOWNLOAD_TIMEOUT_SECONDS, headers={"User-Agent": "Mozilla/5.0"})
        resp.raise_for_status()
        return resp.content.decode("utf-8-sig")
    with open(source, encoding="utf-8-sig") as handle:
        return handle.read()


def parse_feed_text(text: str) -> Iterator[Dict[str, str]]:
    yield from csv.DictReader(io.StringIO(text.lstrip("﻿"), newline=""))


def _to_float(value: Any) -> Optional[float]:
    try:
        return float(str(value).strip().replace(",", "."))
    except (TypeError, ValueError):
        return None


def build_raw_listing(row: Dict[str, str]) -> Optional[Dict[str, Any]]:
    """Converte uma linha do feed no formato de normalize_listing; None se não for aproveitável."""
    item_id = (row.get("itemid") or "").strip()
    title = (row.get("title") or "").strip()
    image_url = (row.get("image_link") or "").strip()
    product_link = (row.get("product_link") or "").strip()
    short_link = (row.get("product_short link") or "").strip()
    if not item_id or not title or not image_url.startswith("https://"):
        return None
    if is_restricted_listing(title):
        return None
    if not _PRODUCT_LINK_RE.match(product_link) or not short_link.startswith(_SHORT_LINK_PREFIX):
        return None

    sale_price = _to_float(row.get("sale_price"))
    list_price = _to_float(row.get("price"))
    rating = _to_float(row.get("item_rating"))
    if not sale_price or not list_price or list_price <= sale_price:
        return None
    if not (MIN_PRICE <= sale_price <= MAX_PRICE):
        return None
    discount = (list_price - sale_price) / list_price * 100
    if not (MIN_DISCOUNT_PERCENT <= discount <= MAX_DISCOUNT_PERCENT):
        return None
    if not rating or rating < MIN_RATING:
        return None

    hint = f"{row.get('global_category1', '')} {row.get('global_category2', '')}"
    return {
        "id": f"{PRODUCT_ID_PREFIX}{item_id}",
        "title": title,
        "price": sale_price,
        "list_price": list_price,
        "url": product_link,
        "affiliate_url": short_link,
        "source": SOURCE_NAME,
        "image_url": image_url,
        "category": category_for(title, hint),
        "rating": rating,
        "free_shipping": 0,
    }


def collect_listings(rows: Iterable[Dict[str, str]]) -> List[Dict[str, Any]]:
    unique: Dict[str, Dict[str, Any]] = {}
    for row in rows:
        listing = build_raw_listing(row)
        if listing:
            unique[listing["id"]] = listing
    return list(unique.values())
