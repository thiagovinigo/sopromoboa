"""Sistema de Gestão e Geração de Links de Afiliados do Só Promo Boa.

Permite:
1. Converter automaticamente URLs raspadas de lojas para links comissionados.
2. Gerenciar tags e IDs de parceiros (Amazon, Magalu, Mercado Livre, Lomadee, Shopee, Awin, etc.).
3. Gerador de links personalizados para campanhas e postagens em redes sociais.
"""
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse, quote
from typing import Optional, Dict, Any

DEFAULT_TAGS = {
    "amazon": {"param": "tag", "default": "thiagovinigo-20"},
    "magalu": {"param": "parceiro", "default": "sopromoboa"},
    "mercadolivre": {"param": "matt_tool", "default": "goth1115110"},
    "shopee": {"param": "utm_source", "default": "an_18356121277"},
    "kabum": {"param": "tag", "default": "sopromoboa"},
    "lomadee": {"param": "sourceId", "default": "2324685"},
}

AWIN_PUBLISHER_ID = "3144638"

AWIN_STORES = {
    "netshoes": {"mid": "11739", "domain": "netshoes.com.br", "name": "Netshoes"},
    "centauro": {"mid": "11674", "domain": "centauro.com.br", "name": "Centauro"},
    "nike": {"mid": "17652", "domain": "nike.com.br", "name": "Nike Brasil"},
    "adidas": {"mid": "19468", "domain": "adidas.com.br", "name": "Adidas Brasil"},
    "decathlon": {"mid": "20257", "domain": "decathlon.com.br", "name": "Decathlon"},
    "drogasil": {"mid": "21841", "domain": "drogasil.com.br", "name": "Drogasil"},
    "drogaraia": {"mid": "21842", "domain": "drogaraia.com.br", "name": "Droga Raia"},
    "fastshop": {"mid": "11822", "domain": "fastshop.com.br", "name": "Fast Shop"},
    "electrolux": {"mid": "16578", "domain": "electrolux.com.br", "name": "Electrolux"},
    "jbl": {"mid": "20739", "domain": "jbl.com.br", "name": "JBL Harman"},
    "samsung": {"mid": "18580", "domain": "samsung.com", "name": "Samsung"},
}


def build_awin_url(
    original_url: str,
    merchant_id: str,
    publisher_id: str = AWIN_PUBLISHER_ID,
    clickref: str = "radar"
) -> str:
    """Gera URL comissionada via Awin para qualquer anunciante parceiro."""
    clean_target = original_url.strip()
    encoded = quote(clean_target, safe="")
    return f"https://www.awin1.com/cread.php?awinmid={merchant_id}&awinaffid={publisher_id}&clickref={clickref}&ued={encoded}"


def detect_store_from_url(url: str) -> str:
    """Identifica a loja/marketplace a partir do domínio da URL."""
    domain = urlparse(url).netloc.lower()

    # Checa primeiro lojas Awin
    for slug, cfg in AWIN_STORES.items():
        if cfg["domain"] in domain:
            return slug

    if "amazon.com" in domain:
        return "amazon"
    if "mercadolivre.com" in domain or "mercado.carrefour" in domain:
        return "mercadolivre"
    if "magazineluiza.com" in domain or "magazinevoce.com" in domain:
        return "magalu"
    if "kabum.com" in domain:
        return "kabum"
    if "shopee.com" in domain or "shope.ee" in domain or "s.shopee" in domain:
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

    # 1. Se for loja da rede Awin
    if store_slug in AWIN_STORES:
        mid = custom_tag or AWIN_STORES[store_slug]["mid"]
        return build_awin_url(original_url, merchant_id=mid, publisher_id=AWIN_PUBLISHER_ID, clickref=utm_source)

    try:
        # Se for um shortlink da Shopee, desempacota para link canônico direto e remove tag de terceiros
        if "s.shopee.com.br" in original_url or "shope.ee" in original_url:
            try:
                import requests, re
                resp = requests.get(original_url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}, timeout=5, allow_redirects=True)
                final_u = resp.url
                m_i = re.search(r'-i\.(\d+)\.(\d+)', final_u)
                m_p = re.search(r'/product/(\d+)/(\d+)', final_u)
                if m_i:
                    original_url = f"https://shopee.com.br/product/{m_i.group(1)}/{m_i.group(2)}"
                elif m_p:
                    original_url = f"https://shopee.com.br/product/{m_p.group(1)}/{m_p.group(2)}"
                else:
                    clean_b = final_u.split("?")[0]
                    if "login" not in clean_b and "verify" not in clean_b:
                        original_url = clean_b
            except Exception:
                pass

        parsed = urlparse(original_url)
        params = parse_qs(parsed.query)

        # Regra específica da Amazon Brasil
        if store_slug == "amazon":
            tag = custom_tag or DEFAULT_TAGS["amazon"]["default"]
            params["tag"] = [tag]
            for clean_key in ["psc", "ref", "qid", "sr"]:
                if clean_key in params and clean_key != "psc":
                    params.pop(clean_key, None)

        # Regra Magazine Luiza
        elif store_slug == "magalu":
            parceiro = custom_tag or DEFAULT_TAGS["magalu"]["default"]
            params["parceiro"] = [parceiro]
            params["tipo"] = ["link"]

        # Regra Mercado Livre
        elif store_slug == "mercadolivre":
            ml_tag = custom_tag or DEFAULT_TAGS["mercadolivre"]["default"]
            params["matt_tool"] = [ml_tag]

        # Regra Shopee
        elif store_slug == "shopee":
            sp_tag = custom_tag or DEFAULT_TAGS["shopee"]["default"]
            params["utm_source"] = [sp_tag]
            params["mmp_pid"] = [sp_tag]
            params["utm_medium"] = ["affiliates"]

        # Outras lojas registradas em DEFAULT_TAGS
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
        "has_partner_tag": bool(store in DEFAULT_TAGS or store in AWIN_STORES or custom_tag)
    }
