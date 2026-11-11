"""Sistema de Gestão e Geração de Links de Afiliados do QuePromo.

Permite:
1. Converter automaticamente URLs raspadas de lojas para links comissionados.
2. Gerenciar tags e IDs de parceiros (Amazon, Magalu, Mercado Livre, Lomadee, Shopee, Awin, etc.).
3. Gerador de links personalizados para campanhas e postagens em redes sociais.
"""
import os
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

AWIN_PUBLISHER_ID = os.environ.get("AWIN_PUBLISHER_ID", "3144638")

# Sites que usam a rede: "quepromo" (este repositório) e "mercagym" (~/buscafitness).
SITE_QUEPROMO = "quepromo"
SITE_MERCAGYM = "mercagym"

# Programas da Awin (conta de publisher 3144638). IDs lidos do painel da Awin em 05/11/2026. Campos:
#   mid           ID do anunciante (awinmid). AWIN_MID_<SLUG> no .env tem prioridade, sem mexer no código.
#   mid_verified  True se o ID foi conferido no painel.
#   status        "approved": o link Awin é aplicado. "pending": candidatura enviada, ainda sem comissão, então o
#                 link original é mantido. "not_requested": ainda não pedimos. "rejected": a Awin recusou (link original mantido).
#                 Quando a Awin aprovar, basta listar o
#                 slug em AWIN_APPROVED no .env (separado por vírgula), sem deploy de código.
#   sites         em quais sites a loja entra ("quepromo", "mercagym").
#   filter_health True se a loja vende medicamento: o feed precisa descartar esses itens (Anvisa RDC 96/2008).
# Os domínios de algumas lojas são prováveis, não confirmados: confira com scripts/awin_verify.py antes de aprovar.
_BOTH = (SITE_QUEPROMO, SITE_MERCAGYM)
_GYM = (SITE_MERCAGYM,)


def _store(mid, domain, name, status, sites, verified=True, filter_health=False):
    return {"mid": mid, "mid_verified": verified, "domain": domain, "name": name,
            "status": status, "sites": sites, "filter_health": filter_health}


AWIN_STORES = {
    "lauriesporte": _store("118977", "lauriesporte.com.br", "Lauri Esporte", "approved", _GYM),
    "centauro": _store("17806", "centauro.com.br", "Centauro", "pending", _BOTH),
    "nike": _store("17652", "nike.com.br", "Nike Brasil", "approved", _BOTH),
    "adidas": _store("79926", "adidas.com.br", "adidas Brasil", "approved", _BOTH),
    "decathlon": _store("19296", "decathlon.com.br", "Decathlon", "approved", _BOTH),
    "asics": _store("23659", "asics.com.br", "ASICS Brasil", "pending", _BOTH),
    "authenticfeet": _store("28775", "authenticfeet.com.br", "Authentic Feet", "pending", _BOTH),
    "technos": _store("28161", "technos.com.br", "Technos", "pending", _BOTH),
    "puma": _store("32675", "puma.com", "PUMA Brasil", "pending", _GYM),
    # Recusada em 10/11/2026 ("URL inativo, página não encontrada"); a Awin só permite recandidatar a partir de 11/12/2026.
    "underarmour": _store("18864", "underarmour.com.br", "Under Armour Brasil", "rejected", _GYM),
    "mizuno": _store("51271", "mizuno.com.br", "Mizuno Brasil", "pending", _GYM),
    "olympikus": _store("17698", "olympikus.com.br", "Olympikus", "pending", _GYM),
    "dafiti": _store("17697", "dafiti.com.br", "Dafiti", "approved", _GYM),
    "pacco": _store("130751", "pacco.com.br", "PACCO", "pending", _GYM),
    "swissmove": _store("125142", "swissmove.com.br", "Swiss Move", "pending", _GYM),
    "electrolux": _store("16578", "electrolux.com.br", "Electrolux", "not_requested", (SITE_QUEPROMO,), verified=False),
}


def awin_mid(slug: str) -> str:
    """ID do anunciante: AWIN_MID_<SLUG> do ambiente tem prioridade sobre o valor da tabela."""
    return os.environ.get(f"AWIN_MID_{slug.upper()}") or AWIN_STORES[slug]["mid"]


def awin_is_approved(slug: str) -> bool:
    """True se a Awin aprovou a loja (campo status ou slug listado em AWIN_APPROVED)."""
    listed = {s.strip().lower() for s in os.environ.get("AWIN_APPROVED", "").split(",") if s.strip()}
    cfg = AWIN_STORES.get(slug)
    return bool(cfg) and (cfg["status"] == "approved" or slug in listed)


def awin_stores_for_site(site: str) -> Dict[str, Dict[str, Any]]:
    """Lojas da Awin que atendem um site ("quepromo" ou "mercagym"), em qualquer status."""
    return {slug: cfg for slug, cfg in AWIN_STORES.items() if site in cfg["sites"]}


def build_awin_url(
    original_url: str,
    merchant_id: str,
    publisher_id: str = AWIN_PUBLISHER_ID,
    clickref: str = "radar"
) -> str:
    """Gera URL comissionada via Awin para qualquer anunciante parceiro."""
    clean_target = original_url.strip()
    if urlparse(clean_target).scheme not in ("http", "https"):
        raise ValueError("URL de destino da Awin precisa ser http(s)")
    mid, pub, ref = (quote(str(v), safe="") for v in (merchant_id, publisher_id, clickref))
    encoded = quote(clean_target, safe="")
    return f"https://www.awin1.com/cread.php?awinmid={mid}&awinaffid={pub}&clickref={ref}&ued={encoded}"


def detect_store_from_url(url: str) -> str:
    """Identifica a loja/marketplace a partir do domínio da URL."""
    domain = urlparse(url).netloc.lower()

    # Checa primeiro lojas Awin, por fronteira de domínio (evita "basics.com.br" casar com "asics.com.br")
    host = (urlparse(url).hostname or "").lower()
    for slug, cfg in AWIN_STORES.items():
        if host == cfg["domain"] or host.endswith("." + cfg["domain"]):
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
    utm_source: str = "quepromo",
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
    # custom_tag é ignorado aqui: o tracking_id de outras redes (Lomadee, Shopee...) não é um awinmid.
    if store_slug in AWIN_STORES and awin_is_approved(store_slug):
        if urlparse(original_url.strip()).scheme in ("http", "https"):
            return build_awin_url(original_url, merchant_id=awin_mid(store_slug),
                                  publisher_id=AWIN_PUBLISHER_ID, clickref=utm_source)

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
        utm_source="quepromo",
        utm_medium="afiliados"
    )
    return {
        "store": store,
        "original_url": raw_url,
        "affiliate_url": affiliate_url,
        "campaign": campaign_name,
        "has_partner_tag": bool(store in DEFAULT_TAGS or awin_is_approved(store) or custom_tag)
    }
