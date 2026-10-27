"""Cliente da API do Mercado Livre: catálogo de produtos mais vendidos com preço real de oferta.

Usa o token de aplicativo (client_credentials) do app "ofertaspromo". A busca de anúncios (/sites/MLB/search)
e /items/{id} respondem 403 para este app, então a coleta parte dos destaques por categoria e lê o preço em
/products/{id}/items. As credenciais vêm de ML_APP_ID e ML_APP_SECRET (backend/.env, fora do git).
"""
import os
import re
import threading
import time
from typing import Any, Dict, Iterable, Iterator, List, Optional, Tuple

import requests
from dotenv import load_dotenv

from category_map import category_for
from content_policy import is_restricted_listing

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))

API_BASE = "https://api.mercadolibre.com"
SITE_ID = "MLB"
REQUEST_TIMEOUT_SECONDS = 25
MIN_REQUEST_INTERVAL_SECONDS = float(os.getenv("ML_MIN_REQUEST_INTERVAL", "0.12"))
MAX_RETRIES = 3
MAX_RETRY_AFTER_SECONDS = 30

PRODUCT_ID_PREFIX = "mlp_"
STORE_NAME = "Mercado Livre"
ITEM_URL_TEMPLATE = "https://produto.mercadolivre.com.br/MLB-{number}"
ITEM_ID_RE = re.compile(r"^MLB(\d+)$")

# Preço fora da faixa costuma ser peça avulsa, erro de cadastro ou anúncio de teste.
MIN_PRICE = 10.0
MAX_PRICE = 50_000.0
# Preço de lista informado pelo vendedor acima disso é inflado: o item entra, mas sem desconto.
MAX_DISCOUNT_PERCENT = 70.0

_rate_lock = threading.Lock()
_last_request_at = 0.0


def get_credentials() -> Optional[Tuple[str, str]]:
    app_id = os.getenv("ML_APP_ID", "").strip()
    secret = os.getenv("ML_APP_SECRET", "").strip()
    return (app_id, secret) if app_id and secret else None


def _wait_for_request_slot() -> None:
    global _last_request_at
    with _rate_lock:
        wait = MIN_REQUEST_INTERVAL_SECONDS - (time.monotonic() - _last_request_at)
        if wait > 0:
            time.sleep(wait)
        _last_request_at = time.monotonic()


def fetch_token(app_id: str, secret: str) -> str:
    resp = requests.post(
        f"{API_BASE}/oauth/token",
        data={"grant_type": "client_credentials", "client_id": app_id, "client_secret": secret},
        timeout=REQUEST_TIMEOUT_SECONDS,
    )
    resp.raise_for_status()
    return resp.json()["access_token"]


class MercadoLivreClient:
    """Sessão autenticada com espaçamento entre requisições e retentativa em 429/5xx."""

    def __init__(self, app_id: str, secret: str) -> None:
        self._app_id = app_id
        self._secret = secret
        self._token = fetch_token(app_id, secret)

    def get(self, path: str, params: Optional[Dict[str, Any]] = None) -> Optional[Any]:
        """JSON da resposta; None quando o recurso não existe ou não está liberado (404/403)."""
        refreshed = False
        for attempt in range(MAX_RETRIES + 1):
            _wait_for_request_slot()
            try:
                resp = requests.get(
                    f"{API_BASE}{path}",
                    params=params,
                    headers={"Authorization": f"Bearer {self._token}"},
                    timeout=REQUEST_TIMEOUT_SECONDS,
                )
            except (requests.ConnectionError, requests.Timeout):
                # O ML derruba conexões em varreduras longas: espera e tenta de novo
                if attempt >= MAX_RETRIES:
                    raise
                time.sleep(2 * (attempt + 1))
                continue
            if resp.status_code == 401 and not refreshed:
                self._token = fetch_token(self._app_id, self._secret)
                refreshed = True
                continue
            if resp.status_code in (429, 500, 502, 503, 504) and attempt < MAX_RETRIES:
                retry_after = float(resp.headers.get("Retry-After") or 2 * (attempt + 1))
                time.sleep(min(retry_after, MAX_RETRY_AFTER_SECONDS))
                continue
            if resp.status_code in (403, 404):
                return None
            resp.raise_for_status()
            return resp.json()
        raise RuntimeError(f"Mercado Livre: falha repetida em {path}")


def item_url(item_id: str) -> str:
    """Página direta do anúncio (nunca busca nem link curto de terceiros)."""
    match = ITEM_ID_RE.match(item_id)
    return ITEM_URL_TEMPLATE.format(number=match.group(1))


def _to_float(value: Any) -> Optional[float]:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def pick_best_offer(offers: Iterable[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """Menor preço entre as ofertas de produto novo com preço válido."""
    valid = []
    for offer in offers:
        price = _to_float(offer.get("price"))
        if price and price > 0 and offer.get("condition", "new") == "new":
            valid.append((price, offer))
    return min(valid, key=lambda pair: pair[0])[1] if valid else None


def _plausible_list_price(price: float, original_price: Any) -> Optional[float]:
    list_price = _to_float(original_price)
    if not list_price or list_price <= price:
        return None
    if (list_price - price) / list_price * 100 > MAX_DISCOUNT_PERCENT:
        return None
    return list_price


def build_raw_listing(
    product: Dict[str, Any], offer: Dict[str, Any], category_name: str
) -> Optional[Dict[str, Any]]:
    """Converte produto + melhor oferta no formato de normalize_listing; None se não for aproveitável."""
    item_id = str(offer.get("item_id") or "")
    if not ITEM_ID_RE.match(item_id) or product.get("status") != "active":
        return None

    title = (product.get("name") or "").strip()
    image_url = next((pic.get("url") for pic in product.get("pictures") or [] if pic.get("url")), None)
    price = _to_float(offer.get("price"))
    if not title or not image_url or not price or not (MIN_PRICE <= price <= MAX_PRICE):
        return None
    if is_restricted_listing(title, f"{STORE_NAME} {category_name}"):
        return None

    return {
        "id": f"{PRODUCT_ID_PREFIX}{item_id}",
        "category": category_for(title, category_name),
        "title": title,
        "price": price,
        "list_price": _plausible_list_price(price, offer.get("original_price")),
        "url": item_url(item_id),
        "source": STORE_NAME,
        "image_url": image_url,
        "free_shipping": int(bool((offer.get("shipping") or {}).get("free_shipping"))),
    }


def collect_product_refs(highlights: Iterable[Tuple[str, Dict[str, Any]]]) -> List[Tuple[str, str]]:
    """(id do produto, categoria) únicos, só de itens de catálogo (PRODUCT), na ordem dos destaques."""
    seen: Dict[str, str] = {}
    for category_name, payload in highlights:
        for entry in (payload or {}).get("content") or []:
            if entry.get("type") == "PRODUCT" and entry.get("id") and entry["id"] not in seen:
                seen[entry["id"]] = category_name
    return [(product_id, category) for product_id, category in seen.items()]


def limit_refs(refs: List[Tuple[str, str]], cap: int) -> List[Tuple[str, str]]:
    """Corta em `cap` intercalando as categorias, para o limite não cair todo sobre a primeira."""
    queues: Dict[str, List[Tuple[str, str]]] = {}
    for ref in refs:
        queues.setdefault(ref[1], []).append(ref)

    selected: List[Tuple[str, str]] = []
    depth = 0
    while len(selected) < cap and any(depth < len(queue) for queue in queues.values()):
        for queue in queues.values():
            if depth < len(queue) and len(selected) < cap:
                selected.append(queue[depth])
        depth += 1
    return selected


def iter_highlights(client: MercadoLivreClient) -> Iterator[Tuple[str, Dict[str, Any]]]:
    """Destaques de cada categoria raiz e de suas subcategorias diretas, rotulados pela categoria raiz."""
    for root in client.get(f"/sites/{SITE_ID}/categories") or []:
        try:
            detail = client.get(f"/categories/{root['id']}") or {}
        except requests.RequestException as err:
            print(f"[Mercado Livre] Categoria {root['id']} ignorada: {err}")
            continue
        node_ids = [root["id"]] + [child["id"] for child in detail.get("children_categories") or []]
        for node_id in node_ids:
            try:
                payload = client.get(f"/highlights/{SITE_ID}/category/{node_id}")
            except requests.RequestException as err:
                print(f"[Mercado Livre] Destaques de {node_id} ignorados: {err}")
                continue
            if payload:
                yield root["name"], payload


def fetch_listing(client: MercadoLivreClient, product_id: str, category_name: str) -> Optional[Dict[str, Any]]:
    product = client.get(f"/products/{product_id}")
    offers = (client.get(f"/products/{product_id}/items") or {}).get("results") or []
    offer = pick_best_offer(offers)
    if not product or not offer:
        return None
    return build_raw_listing(product, offer, category_name)
