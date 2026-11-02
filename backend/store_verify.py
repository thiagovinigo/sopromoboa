"""Confere preço e estoque de cada oferta na própria loja antes de publicá-la.

O feed da Lomadee chega com dados de até 30 dias: preço defasado, produto sem estoque ou página que
saiu do ar. Aqui cada oferta é lida de novo na loja (API pública da VTEX, ou JSON-LD da página) e só
sobrevive o que for confirmado. Preço e preço de lista passam a ser os da loja.
"""
import json
import re
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, Tuple
from urllib.parse import urlparse

OK = "ok"
GONE = "gone"
UNKNOWN = "unknown"

# Acima disso de respostas inconclusivas, tratamos como queda de rede e não mexemos no catálogo.
MAX_UNKNOWN_RATIO = 0.5
DEFAULT_WORKERS = 8
REQUEST_TIMEOUT_SECONDS = 20
_HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; QuePromoBot/1.0; +https://quepromo.com.br)",
    "Accept-Language": "pt-BR,pt;q=0.9",
}

Fetch = Callable[[str], Tuple[int, str]]

_LD_JSON_RE = re.compile(r'<script[^>]*application/ld\+json[^>]*>(.*?)</script>', re.S)


@dataclass(frozen=True)
class LiveOffer:
    price: float
    list_price: Optional[float]


def vtex_api_url(product_url: str) -> str:
    parsed = urlparse(product_url)
    slug = re.sub(r"/p$", "", parsed.path.strip("/"))
    return f"{parsed.scheme}://{parsed.netloc}/api/catalog_system/pub/products/search/{slug}/p"


def _parse_vtex(body: str) -> Tuple[str, Optional[LiveOffer]]:
    try:
        products = json.loads(body)
    except ValueError:
        return UNKNOWN, None
    if not products:
        return UNKNOWN, None

    in_stock = []
    for item in products[0].get("items") or []:
        for seller in item.get("sellers") or []:
            offer = seller.get("commertialOffer") or {}
            if (offer.get("AvailableQuantity") or 0) > 0 and (offer.get("Price") or 0) > 0:
                in_stock.append(offer)
    if not in_stock:
        return GONE, None

    cheapest = min(in_stock, key=lambda offer: offer["Price"])
    price = float(cheapest["Price"])
    list_price = float(cheapest.get("ListPrice") or 0)
    return OK, LiveOffer(price, list_price if list_price > price else None)


def _walk_offers(node: Any):
    if isinstance(node, list):
        for child in node:
            yield from _walk_offers(child)
    elif isinstance(node, dict):
        offers = node.get("offers")
        for offer in offers if isinstance(offers, list) else [offers]:
            if isinstance(offer, dict):
                yield offer
        for child in node.values():
            if isinstance(child, (dict, list)):
                yield from _walk_offers(child)


def _parse_json_ld(html: str) -> Tuple[str, Optional[LiveOffer]]:
    prices: List[float] = []
    for block in _LD_JSON_RE.findall(html):
        try:
            data = json.loads(block)
        except ValueError:
            continue
        for offer in _walk_offers(data):
            if "OutOfStock" in str(offer.get("availability") or ""):
                return GONE, None
            for key in ("price", "lowPrice"):
                try:
                    value = float(offer[key])
                except (KeyError, TypeError, ValueError):
                    continue
                if value > 0:
                    prices.append(value)
    if not prices:
        return UNKNOWN, None
    return OK, LiveOffer(min(prices), None)


def is_redirected_away(requested_url: str, final_url: str) -> bool:
    """True se a loja mandou o cliente para outra página (home, categoria) em vez do produto."""
    requested, final = urlparse(requested_url), urlparse(final_url)
    if requested.netloc.removeprefix("www.") != final.netloc.removeprefix("www."):
        return True
    requested_path, final_path = requested.path.rstrip("/"), final.path.rstrip("/")
    return requested_path != final_path and not final_path.endswith("/p")


def make_image_status(timeout: float = REQUEST_TIMEOUT_SECONDS) -> Callable[[str], int]:
    """Status HTTP da foto sem baixá-la inteira; 0 quando a rede falha."""
    import requests

    def image_status(url: str) -> int:
        try:
            with requests.get(url, headers=_HEADERS, timeout=timeout, stream=True) as resp:
                return resp.status_code
        except requests.RequestException:
            return 0

    return image_status


def make_http_fetch(per_host: int = 2, retries: int = 2, backoff_seconds: float = 3.0) -> Fetch:
    """Fetch real: poucas conexões por loja (evita 429) e nova tentativa quando a loja limita o ritmo."""
    import threading
    import time

    import requests

    gates: Dict[str, threading.Semaphore] = {}
    gates_lock = threading.Lock()

    def gate_for(host: str) -> threading.Semaphore:
        with gates_lock:
            return gates.setdefault(host, threading.Semaphore(per_host))

    def fetch(url: str) -> Tuple[int, str]:
        with gate_for(urlparse(url).netloc):
            for attempt in range(retries + 1):
                try:
                    resp = requests.get(url, headers=_HEADERS, timeout=REQUEST_TIMEOUT_SECONDS)
                except requests.RequestException:
                    return 0, ""
                if resp.status_code != 429 or attempt == retries:
                    if resp.status_code == 200 and is_redirected_away(url, resp.url):
                        return 404, ""
                    return resp.status_code, resp.text
                time.sleep(backoff_seconds * (attempt + 1))
        return 0, ""

    return fetch


def check_listing(raw: Dict[str, Any], fetch: Fetch) -> Tuple[str, Optional[LiveOffer]]:
    """Devolve (OK, oferta ao vivo), (GONE, None) se a loja não vende mais, ou (UNKNOWN, None)."""
    url = raw["url"]
    status, body = fetch(vtex_api_url(url))
    if status == 200:
        verdict, offer = _parse_vtex(body)
        if verdict != UNKNOWN:
            return verdict, offer

    status, body = fetch(url)
    if status in (404, 410):
        return GONE, None
    if status == 200:
        return _parse_json_ld(body)
    return UNKNOWN, None


def _image_is_gone(raw: Dict[str, Any], image_status: Optional[Callable[[str], int]]) -> bool:
    image_url = raw.get("image_url")
    return bool(image_status and image_url and image_status(image_url) in (404, 410))


def verify_listings(
    raws: List[Dict[str, Any]],
    fetch: Fetch,
    workers: int = DEFAULT_WORKERS,
    image_status: Optional[Callable[[str], int]] = None,
) -> List[Dict[str, Any]]:
    """Mantém só as ofertas confirmadas na loja, já com o preço atual. Em queda de rede devolve []."""
    if not raws:
        return []
    with ThreadPoolExecutor(max_workers=workers) as pool:
        verdicts = list(pool.map(lambda raw: check_listing(raw, fetch), raws))
        no_image = list(pool.map(lambda raw: _image_is_gone(raw, image_status), raws))

    unknown = sum(1 for verdict, _ in verdicts if verdict == UNKNOWN)
    if unknown / len(raws) > MAX_UNKNOWN_RATIO:
        print(f"[Verificação] {unknown}/{len(raws)} respostas inconclusivas; catálogo mantido sem alterações.")
        return []

    confirmed = [
        {**raw, "price": offer.price, "list_price": offer.list_price}
        for raw, (verdict, offer), image_gone in zip(raws, verdicts, no_image)
        if verdict == OK and not image_gone
    ]
    gone = sum(1 for verdict, _ in verdicts if verdict == GONE)
    print(
        f"[Verificação] {len(confirmed)} confirmadas, {gone} fora do ar/sem estoque, "
        f"{unknown} inconclusivas, {sum(no_image)} sem foto."
    )
    return confirmed
