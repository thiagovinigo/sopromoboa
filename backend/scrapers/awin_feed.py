"""Feeds de produtos da Awin (CSV, gzip) das lojas aprovadas para o QuePromo: Nike, adidas...

O QuePromo recebe tudo o que a loja vende (o MercaGym é que fica só com o recorte de treino). O endereço de cada
feed funciona como credencial e vem de AWIN_FEED_URL_<LOJA> (backend/.env, fora do git); sem ele o scraper não
faz nada. O link de afiliado não é gravado aqui: o normalizador monta o link Awin com o clickref do QuePromo a
partir da URL da loja, e só para lojas já aprovadas.

Cada loja tem a sua função `scrape_awin_<loja>`, porque o worker descobre os scrapers pelo nome e retira o que
sumiu do feed por prefixo de id (RETIRING_SCRAPERS em scraper_worker.py).
"""
import hashlib
import os
import re
import time
import zlib
from typing import Any, Callable, Dict, Iterable, Iterator, List, Optional
from urllib.parse import urlsplit

import requests

from affiliate import AWIN_STORES, awin_is_approved, awin_stores_for_site, detect_store_from_url
from content_policy import is_restricted_listing
from shopee_feed import _to_float, iter_csv_rows as _iter_plain_csv_rows

SITE = "quepromo"
CATEGORY = "esportes"
ID_PREFIX = "awin"
GZIP_MAGIC = b"\x1f\x8b"
DOWNLOAD_TIMEOUT_SECONDS = (15, 180)
READ_ATTEMPTS = 3
RETRY_WAIT_SECONDS = 20.0
MIN_PRICE = 5.0
MAX_PRICE = 20_000.0
MAX_ITEMS = int(os.getenv("AWIN_FEED_MAX_ITEMS", "10000"))
_IN_STOCK_VALUES = {"1", "true", "yes"}
_NUMBER_RE = re.compile(r"\d[\d.,]*")


def feed_source(slug: str) -> str:
    return os.getenv(f"AWIN_FEED_URL_{slug.upper()}", "").strip()


def _gunzip_if_needed(chunks: Iterable[bytes]) -> Iterator[bytes]:
    """Os feeds da Awin vêm em gzip; descompacta em fluxo se o primeiro pedaço começa com a marca do gzip."""
    decompressor = None
    first = True
    for chunk in chunks:
        if first:
            first = False
            if chunk[:2] == GZIP_MAGIC:
                decompressor = zlib.decompressobj(zlib.MAX_WBITS | 16)
        yield decompressor.decompress(chunk) if decompressor else chunk
    if decompressor:
        yield decompressor.flush()


def iter_csv_rows(chunks: Iterable[bytes]) -> Iterator[Dict[str, str]]:
    yield from _iter_plain_csv_rows(_gunzip_if_needed(chunks))


def iter_feed_rows(source: str) -> Iterator[Dict[str, str]]:
    """Linhas do CSV de uma URL https ou de um arquivo local, em fluxo, com ou sem gzip."""
    if source.startswith("https://"):
        response = requests.get(source, stream=True, timeout=DOWNLOAD_TIMEOUT_SECONDS,
                                headers={"User-Agent": "QuePromoBot/1.0"})
        try:
            response.raise_for_status()
            yield from iter_csv_rows(response.iter_content(chunk_size=1 << 20))
        finally:
            response.close()
        return
    with open(source, "rb") as handle:
        yield from iter_csv_rows(iter(lambda: handle.read(1 << 20), b""))


def _price(value: Optional[str]) -> Optional[float]:
    """Preço do feed: '99.99', '99,99' ou '149.99  BRL' (a Awin às vezes deixa a moeda no fim)."""
    found = _NUMBER_RE.search(value or "")
    return _to_float(found.group(0)) if found else None


def _in_stock(row: Dict[str, str]) -> bool:
    """Alguns feeds trazem `in_stock` (1/0), outros `stock_status` ("in stock"); sem nenhuma das duas, não entra."""
    if (row.get("in_stock") or "").strip().lower() in _IN_STOCK_VALUES:
        return True
    return (row.get("stock_status") or "").strip().lower() == "in stock"


def _page_key(url: str) -> str:
    """Identificador estável da página do produto (sem query): o feed repete a mesma peça por tamanho e cor."""
    parts = urlsplit(url)
    return hashlib.sha1(f"{parts.netloc}{parts.path}".encode("utf-8")).hexdigest()[:12]


def build_raw_listing(row: Dict[str, str]) -> Optional[Dict[str, Any]]:
    """Converte uma linha do feed em listing; None se a loja não é aprovada para o QuePromo ou o item não é vendável."""
    product_id = (row.get("aw_product_id") or "").strip()
    title = (row.get("product_name") or "").strip()
    url = (row.get("merchant_deep_link") or "").strip()
    if url.startswith("http://"):
        url = "https://" + url[len("http://"):]  # os feeds da adidas vêm em http, mas a loja atende em https
    image_url = (row.get("merchant_image_url") or row.get("aw_image_url") or "").strip()
    if not product_id or not title or not url.startswith("https://") or not image_url.startswith("https://"):
        return None
    if not _in_stock(row) or is_restricted_listing(title):
        return None

    store_slug = detect_store_from_url(url)
    if store_slug not in awin_stores_for_site(SITE) or not awin_is_approved(store_slug):
        return None
    price = _price(row.get("search_price"))
    if not price or not (MIN_PRICE <= price <= MAX_PRICE):
        return None

    list_price = _price(row.get("product_price_old")) or _price(row.get("rrp_price"))
    store = AWIN_STORES[store_slug]
    return {
        "id": f"{ID_PREFIX}{store_slug}_{_page_key(url)}",
        "title": title,
        "category": CATEGORY,  # lojas de marca esportiva: o título não decide (evita tênis em "periféricos")
        "brand": (row.get("brand_name") or "").strip() or store["name"],
        "price": price,
        "list_price": list_price if list_price and list_price > price else None,
        "url": url,
        "source": store["name"],
        "image_url": image_url,
        "free_shipping": 0,
    }


def collect_listings(rows: Iterable[Dict[str, str]], store_slug: str) -> List[Dict[str, Any]]:
    """Listings da loja pedida, sem repetição (a mesma peça aparece uma vez por tamanho no feed)."""
    prefix = f"{ID_PREFIX}{store_slug}_"
    unique: Dict[str, Dict[str, Any]] = {}
    for row in rows:
        listing = build_raw_listing(row)
        if listing and listing["id"].startswith(prefix):
            unique.setdefault(listing["id"], listing)
    return list(unique.values())[:MAX_ITEMS]


def read_store_listings(store_slug: str, attempts: int = READ_ATTEMPTS, wait_seconds: float = RETRY_WAIT_SECONDS,
                        sleep: Callable[[float], None] = time.sleep) -> List[Dict[str, Any]]:
    """Lê o feed da loja; só falha de rede merece nova tentativa. Feed ilegível devolve vazio e o catálogo é mantido."""
    source = feed_source(store_slug)
    if not source:
        print(f"[Awin Feed] AWIN_FEED_URL_{store_slug.upper()} ausente; nada a coletar.")
        return []
    for attempt in range(1, attempts + 1):
        try:
            listings = collect_listings(iter_feed_rows(source), store_slug)
            print(f"[Awin Feed] {store_slug}: {len(listings)} itens aproveitados.")
            return listings
        except Exception as err:
            print(f"[Awin Feed] {store_slug}: falha ao ler o feed ({type(err).__name__}), tentativa {attempt} de {attempts}.")
            if not isinstance(err, requests.RequestException) or attempt == attempts:
                break
            sleep(wait_seconds * attempt)
    return []


def scrape_awin_nike() -> List[Dict[str, Any]]:
    return read_store_listings("nike")


def scrape_awin_adidas() -> List[Dict[str, Any]]:
    return read_store_listings("adidas")
