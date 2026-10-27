"""Cliente da API de afiliados da Lomadee: catálogo de produtos e links comissionados.

Documentação: https://docs.lomadee.com.br — limite de 60 requisições por minuto por chave.
A chave vem da variável de ambiente LOMADEE_API_KEY (arquivo backend/.env, fora do git).
"""
import hashlib
import os
import threading
import time
from datetime import datetime, timezone
from typing import Any, Dict, Iterable, Iterator, List, Optional
from urllib.parse import urlparse

import requests
from dotenv import load_dotenv

from category_map import category_for
from content_policy import is_restricted_listing

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))

API_BASE = "https://api.lomadee.com.br"
REQUEST_TIMEOUT_SECONDS = 30
CLICK_TIMEOUT_SECONDS = 8  # geração de link no clique do usuário não pode travar o redirecionamento
MIN_REQUEST_INTERVAL_SECONDS = 1.05  # 60 req / 60 s por chave
MAX_RETRIES_ON_RATE_LIMIT = 3
MAX_RETRY_AFTER_SECONDS = 60
PRODUCTS_PAGE_SIZE = 100
BRANDS_PAGE_SIZE = 20
MAX_BRAND_PAGES = 50
BRANDS_CACHE_TTL_SECONDS = 12 * 3600

PRODUCT_ID_PREFIX = "lmd_"
SHORT_LINK_HOSTS = ("lmdee.link",)
PREFERRED_CHANNEL_NAME = "Que Promo"

# Filtros de qualidade: descontos fora dessa faixa costumam ser preço de lista inflado ou erro de cadastro.
MIN_PRICE = 10.0
MAX_PRICE = 50_000.0
MIN_DISCOUNT_PERCENT = 10.0
MAX_DISCOUNT_PERCENT = 70.0
# Idade máxima dos dados do feed (updatedAt). Medido em out/2026: mediana de 73 dias e só 16% atualizados na semana.
MAX_DATA_AGE_DAYS = float(os.getenv("LOMADEE_MAX_DATA_AGE_DAYS", "14"))

_rate_lock = threading.Lock()
_last_request_at = 0.0
_brand_cache_lock = threading.Lock()
_brand_cache: Dict[str, Any] = {"loaded_at": 0.0, "ids_by_name": {}}


def get_api_key() -> Optional[str]:
    key = os.getenv("LOMADEE_API_KEY", "").strip()
    return key or None


def get_links_api_key() -> Optional[str]:
    """Chave só com escopo do encurtador (menor privilégio); cai na chave principal se não houver."""
    return os.getenv("LOMADEE_LINKS_API_KEY", "").strip() or get_api_key()


def _wait_for_request_slot() -> None:
    global _last_request_at
    with _rate_lock:
        wait = MIN_REQUEST_INTERVAL_SECONDS - (time.monotonic() - _last_request_at)
        if wait > 0:
            time.sleep(wait)
        _last_request_at = time.monotonic()


def _request(
    method: str,
    path: str,
    api_key: str,
    *,
    params: Optional[Dict[str, Any]] = None,
    json_body: Optional[Dict[str, Any]] = None,
    timeout: float = REQUEST_TIMEOUT_SECONDS,
) -> Any:
    """Chamada autenticada com espaçamento entre requisições e retentativa em 429."""
    for attempt in range(MAX_RETRIES_ON_RATE_LIMIT + 1):
        _wait_for_request_slot()
        resp = requests.request(
            method,
            f"{API_BASE}{path}",
            headers={"x-api-key": api_key},
            params=params,
            json=json_body,
            timeout=timeout,
        )
        if resp.status_code == 429 and attempt < MAX_RETRIES_ON_RATE_LIMIT:
            retry_after = float(resp.headers.get("Retry-After") or 5)
            time.sleep(min(retry_after, MAX_RETRY_AFTER_SECONDS))
            continue
        resp.raise_for_status()
        return resp.json()
    raise RuntimeError(f"Lomadee: limite de requisições excedido em {path}")


def fetch_brands(api_key: str) -> List[Dict[str, Any]]:
    brands: List[Dict[str, Any]] = []
    for page in range(1, MAX_BRAND_PAGES + 1):
        body = _request(
            "GET", "/affiliate/brands", api_key,
            params={"page": page, "limit": BRANDS_PAGE_SIZE},
        )
        data = body.get("data") or []
        if not data:
            break
        brands.extend(data)
    return brands


def index_brands(brands: Iterable[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    return {brand["id"]: brand for brand in brands if brand.get("id")}


def iter_products(api_key: str, max_pages: int) -> Iterator[Dict[str, Any]]:
    """Percorre o catálogo página a página até esgotar ou atingir max_pages."""
    for page in range(1, max_pages + 1):
        body = _request(
            "GET", "/affiliate/products", api_key,
            params={"page": page, "limit": PRODUCTS_PAGE_SIZE},
        )
        data = body.get("data") or []
        if not data:
            return
        yield from data


def _to_float(value: Any) -> Optional[float]:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _first_pricing(product: Dict[str, Any]) -> Optional[tuple]:
    """Primeiro preço positivo, priorizando variantes disponíveis. Valores vêm em reais."""
    options = sorted(product.get("options") or [], key=lambda opt: not opt.get("available", True))
    for option in options:
        for pricing in option.get("pricing") or []:
            price = _to_float(pricing.get("price"))
            if price and price > 0:
                return price, _to_float(pricing.get("listPrice"))
    return None


def _discount_percent(price: float, list_price: float) -> float:
    return (list_price - price) / list_price * 100


def _data_age_days(product: Dict[str, Any], now: datetime) -> Optional[float]:
    """Idade, em dias, da última atualização do produto no feed da loja (campo updatedAt)."""
    raw = product.get("updatedAt")
    if not raw:
        return None
    try:
        updated = datetime.fromisoformat(str(raw).replace("Z", "+00:00"))
    except ValueError:
        return None
    if updated.tzinfo is None:
        updated = updated.replace(tzinfo=timezone.utc)
    return (now - updated).total_seconds() / 86400


def _listing_id(product_id: str) -> str:
    digest = hashlib.md5(str(product_id).encode("utf-8")).hexdigest()[:12]
    return f"{PRODUCT_ID_PREFIX}{digest}"


def build_raw_listing(product: Dict[str, Any], brand: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """Converte um produto da API no formato aceito por normalize_listing; None se não for aproveitável."""
    if not brand or not (brand.get("network") or {}).get("active"):
        return None
    # Marca sem link liberado para o canal = sem aprovação: o produto não geraria comissão
    if not pick_short_url(brand.get("channels") or []):
        return None
    if not product.get("available") or not product.get("id"):
        return None
    # Feeds de lojas ficam meses sem atualizar: preço antigo não é preço atual
    age_days = _data_age_days(product, datetime.now(timezone.utc))
    if age_days is None or age_days > MAX_DATA_AGE_DAYS:
        return None

    url = product.get("url") or ""
    title = (product.get("name") or "").strip()
    image_url = next((img.get("url") for img in product.get("images") or [] if img.get("url")), None)
    pricing = _first_pricing(product)
    if not url.startswith("https://") or not title or not image_url or not pricing:
        return None
    if is_restricted_listing(title, f"{brand['name']} {brand.get('segment') or ''}"):
        return None

    price, list_price = pricing
    if not (MIN_PRICE <= price <= MAX_PRICE) or not list_price or list_price <= price:
        return None
    if not (MIN_DISCOUNT_PERCENT <= _discount_percent(price, list_price) <= MAX_DISCOUNT_PERCENT):
        return None

    return {
        "id": _listing_id(product["id"]),
        "category": category_for(title, f"{brand['name']} {brand.get('segment') or ''}"),
        "title": title,
        "price": price,
        "list_price": list_price,
        "url": url,
        "source": brand["name"],
        "image_url": image_url,
        "free_shipping": 0,
    }


def collect_listings(
    brands_by_id: Dict[str, Dict[str, Any]], products: Iterable[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    unique: Dict[str, Dict[str, Any]] = {}
    for product in products:
        brand = brands_by_id.get(product.get("organizationId"))
        listing = build_raw_listing(product, brand)
        if listing:
            unique[listing["id"]] = listing
    return list(unique.values())


def select_listings(
    listings: Iterable[Dict[str, Any]], *, per_brand_cap: int, total_cap: int, group_key: str = "source"
) -> List[Dict[str, Any]]:
    """Limita por grupo (maiores descontos primeiro) e intercala os grupos para manter diversidade.

    O grupo é a loja por padrão; use group_key="category" quando todas as ofertas são da mesma loja.
    """
    by_group: Dict[str, List[Dict[str, Any]]] = {}
    for listing in listings:
        by_group.setdefault(listing[group_key], []).append(listing)

    queues = [
        sorted(items, key=lambda x: _discount_percent(x["price"], x["list_price"]), reverse=True)[:per_brand_cap]
        for items in by_group.values()
    ]

    selected: List[Dict[str, Any]] = []
    depth = 0
    while len(selected) < total_cap and any(depth < len(queue) for queue in queues):
        for queue in queues:
            if depth < len(queue) and len(selected) < total_cap:
                selected.append(queue[depth])
        depth += 1
    return selected


def is_short_link(url: Optional[str]) -> bool:
    return bool(url) and (urlparse(url).hostname or "") in SHORT_LINK_HOSTS


def pick_short_url(channels: Iterable[Dict[str, Any]]) -> Optional[str]:
    """Escolhe o link curto do canal do site; canais bloqueados (sem shortUrls) são ignorados."""
    candidates = [ch for ch in channels if ch.get("shortUrls")]
    for channel in candidates:
        if channel.get("name") == PREFERRED_CHANNEL_NAME:
            return channel["shortUrls"][0]
    return candidates[0]["shortUrls"][0] if candidates else None


def create_short_link(
    api_key: str, organization_id: str, product_url: str, timeout: float = REQUEST_TIMEOUT_SECONDS
) -> Optional[str]:
    body = _request(
        "POST", "/affiliate/shortener/url", api_key,
        json_body={"organizationId": organization_id, "type": "Custom", "url": product_url},
        timeout=timeout,
    )
    channels = body if isinstance(body, list) else body.get("data") or []
    return pick_short_url(channels)


def _brand_ids_by_name(api_key: str) -> Dict[str, str]:
    with _brand_cache_lock:
        fresh = time.monotonic() - _brand_cache["loaded_at"] < BRANDS_CACHE_TTL_SECONDS
        if fresh and _brand_cache["ids_by_name"]:
            return _brand_cache["ids_by_name"]
        ids_by_name = {b["name"]: b["id"] for b in fetch_brands(api_key) if b.get("id") and b.get("name")}
        _brand_cache.update(loaded_at=time.monotonic(), ids_by_name=ids_by_name)
        return ids_by_name


def affiliate_link_for_product(store_name: str, product_url: str) -> Optional[str]:
    """Gera o link comissionado de um produto no clique; None se algo falhar (o chamador usa a URL direta)."""
    catalog_key = get_api_key()
    links_key = get_links_api_key()
    if not catalog_key or not links_key:
        return None
    try:
        organization_id = _brand_ids_by_name(catalog_key).get(store_name)
        if not organization_id:
            return None
        return create_short_link(links_key, organization_id, product_url, timeout=CLICK_TIMEOUT_SECONDS)
    except (requests.RequestException, RuntimeError, ValueError) as err:
        print(f"[Lomadee] Falha ao gerar link para {store_name}: {err}")
        return None
