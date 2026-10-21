"""Normalização de dados, categorização inteligente e extração de marcas/especificações.

Trata títulos brutos raspados de diferentes lojas para garantir consistência
na base de dados e nos filtros do front-end.
"""
import re
from typing import Dict, Any, Tuple, Optional
from pricing import calculate_discount_percent
from affiliate import build_affiliate_url, detect_store_from_url

# Mapeamento de categorias e palavras-chave
CATEGORY_RULES = [
    (
        "smartphones",
        [
            r"\biphone\b", r"\bgalaxy\b", r"\bsmartphone\b", r"\bcelular\b",
            r"\bmotorola\b", r"\bredmi\b", r"\bpoco\b", r"\bxiaomi\b", r"\brealme\b"
        ]
    ),
    (
        "informatica",
        [
            r"\bnotebook\b", r"\blaptop\b", r"\bmacbook\b", r"\bcomputador\b",
            r"\bssd\b", r"\bnvme\b", r"\bmonitor\b", r"\bteclado\b", r"\bmouse\b",
            r"\bryzen\b", r"\bintel core\b", r"\brtx\b", r"\brx \d{3,4}\b",
            r"\bplaca de v[ií]deo\b", r"\bmem[oó]ria ram\b", r"\broteador\b"
        ]
    ),
    (
        "eletronicos",
        [
            r"\bsmart tv\b", r"\btv \d{2}\b", r"\bfone de ouvido\b", r"\bheadphone\b",
            r"\bheadset\b", r"\bairpods\b", r"\becho dot\b", r"\balexa\b",
            r"\bkindle\b", r"\bsoundbar\b", r"\bcaixa de som\b", r"\bjbl\b",
            r"\bprojetor\b", r"\bsmartwatch\b", r"\brel[oó]gio inteligente\b"
        ]
    ),
    (
        "games",
        [
            r"\bplaystation\b", r"\bps5\b", r"\bps4\b", r"\bxbox\b", r"\bnintendo switch\b",
            r"\bdualshock\b", r"\bdualsense\b", r"\bconsole\b", r"\bjogo ps\b",
            r"\bcontrole sem fio\b", r"\bgamer\b"
        ]
    ),
    (
        "eletrodomesticos",
        [
            r"\bair fryer\b", r"\bfritadeira\b", r"\bcafeteira\b", r"\bnespresso\b",
            r"\baspirador\b", r"\brob[oô] aspirador\b", r"\bgeladeira\b", r"\brefrigerador\b",
            r"\bm[aá]quina de lavar\b", r"\blava e seca\b", r"\bmicro-?ondas\b",
            r"\bventilador\b", r"\bar-condicionado\b"
        ]
    ),
    (
        "casa",
        [
            r"\bjogo de panelas\b", r"\bpanela de press[aã]o\b", r"\bcolch[aã]o\b",
            r"\btravesseiro\b", r"\bparafusadeira\b", r"\bferramenta\b", r"\bl[aâ]mpada smart\b"
        ]
    ),
]

BRANDS = [
    "Apple", "Samsung", "Xiaomi", "Motorola", "LG", "Sony", "Dell", "Lenovo",
    "Asus", "Acer", "HP", "JBL", "Logitech", "Razer", "Kingston", "Corsair",
    "Mondial", "Philco", "Britânia", "Electrolux", "Brastemp", "Consul",
    "Philips", "Walita", "TCL", "Positivo", "HyperX", "Anker", "Baseus"
]

SPAM_PATTERNS = [
    r"\[\s*(frete gr[aá]tis|promo[cç][aã]o|oferta rel[aâ]mpago|imperd[ií]vel|menor pre[cç]o|original|novo)\s*\]",
    r"\(\s*(frete gr[aá]tis|promo[cç][aã]o|original)\s*\)",
    r"\b100%\s*original\b",
    r"\bpronta entrega\b",
    r"\benvio imediato\b",
]


def clean_title(title: str) -> str:
    """Remove palavras apelativas de anúncio, emojis e excessos de espaço."""
    if not title:
        return ""

    cleaned = title
    for pattern in SPAM_PATTERNS:
        cleaned = re.sub(pattern, "", cleaned, flags=re.IGNORECASE)

    # Remove múltiplos espaços
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned


def detect_category(title: str, hint: Optional[str] = None) -> str:
    """Classifica a categoria do produto a partir do título."""
    if not title:
        return hint or "geral"

    text = title.lower()
    for cat, patterns in CATEGORY_RULES:
        for pat in patterns:
            if re.search(pat, text):
                return cat

    return hint or "geral"


def detect_brand(title: str) -> Optional[str]:
    """Identifica a marca presente no título."""
    if not title:
        return None

    text = title.lower()
    for brand in BRANDS:
        pattern = r"\b" + re.escape(brand.lower()) + r"\b"
        if re.search(pattern, text):
            return brand

    return None


def normalize_listing(raw: Dict[str, Any]) -> Dict[str, Any]:
    """Normaliza um anúncio extraído por qualquer scraper."""
    title = clean_title(raw.get("title", ""))
    price = float(raw.get("price", 0.0))
    list_price = raw.get("list_price")
    if list_price is not None:
        try:
            list_price = float(list_price)
            if list_price <= price:
                list_price = None
        except (ValueError, TypeError):
            list_price = None

    url = raw.get("url", "")
    source = raw.get("source") or detect_store_from_url(url).capitalize()
    category = raw.get("category") or detect_category(title)
    brand = raw.get("brand") or detect_brand(title)
    
    # Gera link comissionado se não fornecido
    affiliate_url = raw.get("affiliate_url") or build_affiliate_url(url, store_slug=source.lower())

    # Desconto
    discount = calculate_discount_percent(price, list_price=list_price)

    return {
        "id": raw["id"],
        "title": title,
        "price": round(price, 2),
        "list_price": round(list_price, 2) if list_price else None,
        "discount_percent": discount,
        "brand": brand,
        "category": category,
        "subcategory": raw.get("subcategory"),
        "url": url,
        "affiliate_url": affiliate_url,
        "source": source,
        "image_url": raw.get("image_url", ""),
        "coupon_code": raw.get("coupon_code"),
        "free_shipping": int(bool(raw.get("free_shipping", 0))),
        "rating": raw.get("rating"),
        "review_count": int(raw.get("review_count", 0)),
        "is_available": int(raw.get("is_available", 1)),
    }
