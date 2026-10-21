"""Sistema de Gestão e Geração de Links de Afiliados do Só Promo Boa.

Permite:
1. Converter automaticamente URLs raspadas de lojas para links comissionados.
2. Gerenciar tags e IDs de parceiros (Amazon, Magalu, Mercado Livre, Lomadee, Shopee, etc.).
3. Gerador de links personalizados para campanhas e postagens em redes sociais.
"""
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
from typing import Optional, Dict, Any

DEFAULT_TAGS = {
    "amazon": {"param": "tag", "default": "sopromoboa-20"},
    "magalu": {"param": "parceiro", "default": "sopromoboa"},
    "mercadolivre": {"param": "matt_tool", "default": "sopromoboa_ml"},
    "shopee": {"param": "af_siteid", "default": "sopromoboa_sp"},
    "kabum": {"param": "tag", "default": "sopromoboa"},
}


def detect_store_from_url(url: str) -> str:
    """Identifica a loja/marketplace a partir do domínio da URL."""
    domain = urlparse(url).netloc.lower()
    if "amazon.com" in domain:
        return "amazon"
    if "mercadolivre.com" in domain or "mercado.carrefour" in domain:
        return "mercadolivre"
    if "magazineluiza.com" in domain or "magazinevoce.com" in domain:
        return "magalu"
    if "kabum.com" in domain:
        return "kabum"
    if "shopee.com" in domain:
        return "shopee"
    if "terabyteshop.com" in domain:
        return "terabyte"
    if "pichau.com" in domain:
        return "pichau"
    if "casasbahia.com" in domain:
        return "casasbahia"
    return "outros"


def build_affiliate_url(
    original_url: str,
    store_slug: Optional[str] = None,
    custom_tag: Optional[str] = None,
    utm_source: str = "sopromoboa",
    utm_medium: str = "web"
) -> str:
    """Aplica as tags de afiliado e UTMs na URL do produto.

    Garante que tags antigas sejam substituídas e a estrutura do link seja preservada.
    """
    if not original_url:
        return ""

    if not store_slug:
        store_slug = detect_store_from_url(original_url)

    try:
        parsed = urlparse(original_url)
        params = parse_qs(parsed.query)

        # 1. Regra específica da Amazon Brasil
        if store_slug == "amazon":
            tag = custom_tag or DEFAULT_TAGS["amazon"]["default"]
            params["tag"] = [tag]
            # Limpa parâmetros temporários desnecessários
            for clean_key in ["psc", "ref", "qid", "sr"]:
                if clean_key in params and clean_key != "psc":
                    params.pop(clean_key, None)

        # 2. Regra Magazine Luiza
        elif store_slug == "magalu":
            parceiro = custom_tag or DEFAULT_TAGS["magalu"]["default"]
            params["parceiro"] = [parceiro]
            params["tipo"] = ["link"]

        # 3. Regra Mercado Livre
        elif store_slug == "mercadolivre":
            ml_tag = custom_tag or DEFAULT_TAGS["mercadolivre"]["default"]
            params["matt_tool"] = [ml_tag]

        # 4. Outras lojas
        elif store_slug in DEFAULT_TAGS:
            cfg = DEFAULT_TAGS[store_slug]
            params[cfg["param"]] = [custom_tag or cfg["default"]]

        # Adiciona rastreamento UTM padrão
        params["utm_source"] = [utm_source]
        params["utm_medium"] = [utm_medium]
        params["utm_campaign"] = ["promocao_radar"]

        # Reconstrói a URL mantendo path limpo
        new_query = urlencode(params, doseq=True)
        return urlunparse((
            parsed.scheme or "https",
            parsed.netloc,
            parsed.path,
            parsed.params,
            new_query,
            parsed.fragment
        ))
    except Exception:
        return original_url


def create_managed_link(
    raw_url: str,
    campaign_name: Optional[str] = "radar",
    custom_tag: Optional[str] = None
) -> Dict[str, Any]:
    """Gera dados completos de um link comissionado para gestão de afiliados."""
    store = detect_store_from_url(raw_url)
    affiliate_url = build_affiliate_url(
        raw_url,
        store_slug=store,
        custom_tag=custom_tag,
        utm_source="sopromoboa",
        utm_medium="afiliados"
    )
    return {
        "store": store,
        "original_url": raw_url,
        "affiliate_url": affiliate_url,
        "campaign": campaign_name,
        "has_partner_tag": bool(store in DEFAULT_TAGS or custom_tag)
    }
