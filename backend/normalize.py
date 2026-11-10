"""Normalização de dados, categorização inteligente e extração de marcas/especificações.

Trata títulos brutos raspados de diferentes lojas para garantir consistência
na base de dados e nos filtros do front-end.
"""
import re
from typing import Dict, Any, Tuple, Optional, List
from pricing import calculate_discount_percent
from affiliate import build_affiliate_url, detect_store_from_url
from text_utils import fold_text

# Padrões que indicam que o item é um acessório/peça compatível e NÃO o aparelho principal
ACCESSORY_TITLE_PATTERNS = [
    r"\bcapinha\b",
    r"^capa\b",
    r"\bcapa\s+(protetora|anti\s*impacto|silicone|magsafe|transparente|carteira|magn[eé]tica|refor[cç]ada|aveludada|couro|para|p/|celular|iphone|galaxy|samsung|xiaomi|redmi|motorola|tablet|ipad|kindle)\b",
    r"^case\b",
    r"\bcase\s+(protetora|anti\s*impacto|silicone|magsafe|transparente|magn[eé]tica|para|p/|celular|iphone|galaxy|ipad|airpods)\b",
    r"\bpel[ií]cula\b",
    r"\bprotetor\s+de\s+(tela|lente|c[aâ]mera|cabo)\b",
    r"\blente\s+(protetora|c[aâ]mera)\b",
    r"^cabo\b",
    r"\bcabo\s+(usb|tipo\s*c|type\s*c|lightning|carregador|de\s+dados|turbo|nylon|tran[cç]ado|hdmi|auxiliar|p2|p10|otg|adaptador|para|p/|iphone)\b",
    r"^carregador\b",
    r"\bcarregador\s+(turbo|r[aá]pido|sem\s+fio|induc[aã]o|magsafe|veicular|port[aá]til|de\s+parede|usb|tipo\s*c|para|p/|iphone|celular|samsung|xiaomi|motorola|bateria|pilha)\b",
    r"\bfonte\s+(carregador|carregadora|turbo|usb|tipo\s*c|\d{2,3}w\s+para|para\s+iphone|para\s+celular|para\s+samsung)\b",
    r"\badaptador\b",
    r"\bleitor\s+de\s+cart[aã]o\b",
    r"\bhub\s+usb\b",
    r"\bconversor\b",
    r"^suporte\b",
    r"\bsuporte\s+(para|p/|de\s+mesa|de\s+parede|veicular|celular|monitor|tv|notebook|tablet|articulado|magn[eé]tico)\b",
    r"\bbra[cç]o\s+articulado\b",
    r"\btrip[eé]\b",
    r"\bring\s*light\b",
    r"\bpau\s+de\s+selfie\b",
    r"\bbast[aã]o\s+de\s+selfie\b",
    r"\bmicrofone\s+(de\s+)?lapela\b",
    r"\bmicrofone\s+(sem\s+fio|s/\s*fio)\b",
    r"\bcontrole\s+gamepad\b",
    r"\bgamepad\b",
    r"\bgatilho\s+(para\s+celular|gamer|mobile)\b",
    r"\bcooler\s+(para\s+celular|mobile|magn[eé]tico)\b",
    r"\bdedeira\b",
    r"^pulseira\b",
    r"\bpulseira\s+(compat[ií]vel|para|p/|de\s+silicone|milanese|nylon|couro|smartwatch|apple\s+watch|mi\s+band|galaxy\s+watch)\b",
    r"\bcaneta\s+(touch|stylus|capacitiva|para\s+ipad|para\s+tablet)\b",
    r"\bpopsocket\b",
    r"\bpop\s+socket\b",
    r"\bchaveiro\b",
    r"\bcord[aã]o\s+de\s+pesco[cç]o\b",
    r"\bbolsa\s+imperme[aá]vel\b",
    r"\bbra[cç]adeira\s+corrida\b",
    r"\btela\s+(frontal|lcd|oled|display|touch)\b",
    r"\bdisplay\s+(frontal|lcd|oled|touch)\b",
    r"\btampa\s+traseira\b",
    r"\bbateria\s+(interna|de\s+reposi[cç][aã]o|compat[ií]vel)\b",
    r"\bconector\s+de\s+carga\b",
    r"\bflex\s+de\s+carga\b",
    r"\bgaveta\s+(de\s+)?chip\b",
    r"\bbandeja\s+(de\s+)?chip\b",
    # Preposição indicando compatibilidade com o aparelho (ex.: "para iPhone 15", "p/ iPhone 15/16", "compatível com Galaxy S24")
    r"\b(para|p/|compat[ií]vel\s+com|compat[ií]vel\s+p/|for)\s+(o\s+|a\s+|os\s+)?(apple\s+|samsung\s+|xiaomi\s+|motorola\s+|android\s+e\s+)?(iphone|galaxy|redmi|poco|moto\s+g|motorola|celular|smartphone|ipad|tablet|macbook|notebook|airpods|apple\s+watch|ps5|ps4|playstation|xbox|nintendo\s+switch)\b",
    # Lista de múltiplos modelos de iPhone/Galaxy no mesmo título (típico de capinhas/películas/cabos)
    r"\biphone\s+\d{1,2}\s*[/,\s]\s*\d{1,2}\s*[/,\s]\s*\d{1,2}\b",
    r"\b\d{1,2}\s*/\s*\d{1,2}\s*/\s*\d{1,2}\s*(pro|max|plus|iphone)?\b",
]

ACCESSORY_QUERY_KEYWORDS = {
    "capa", "capinha", "case", "pelicula", "película", "protetor", "lente",
    "cabo", "carregador", "fonte", "adaptador", "leitor", "hub", "conversor",
    "suporte", "braco", "braço", "articulado", "tripe", "tripé", "lapela",
    "microfone", "gamepad", "controle", "gatilho", "cooler", "dedeira",
    "pulseira", "alca", "alça", "caneta", "stylus", "popsocket", "chaveiro",
    "cordao", "cordão", "bateria", "tela", "display", "tampa", "conector",
    "flex", "gaveta", "bandeja", "acessorio", "acessório", "fone", "headset",
}


def is_accessory_title(title: str) -> bool:
    """Retorna True se o título descreve um acessório, cabo, capa, película ou peça compatível."""
    if not title:
        return False
    text = title.lower().strip()
    for pat in ACCESSORY_TITLE_PATTERNS:
        if re.search(pat, text):
            return True
    return False


def query_wants_accessory(query: str) -> bool:
    """Retorna True se o usuário digitou explicitamente um termo de acessório na busca."""
    if not query:
        return False
    tokens = {t.lower().strip() for t in re.split(r"[\s\-_/,]+", query) if t.strip()}
    return bool(tokens & ACCESSORY_QUERY_KEYWORDS)


def min_plausible_device_price(query: str) -> float:
    """Retorna um piso mínimo de preço coerente quando o usuário busca um aparelho principal (e não um acessório)."""
    if not query or query_wants_accessory(query):
        return 0.0
    q_norm = query.lower().strip()
    if re.search(r"\b(iphone|macbook|ps5|playstation\s*5|xbox\s+series|rtx\s*\d{4}|rx\s*\d{4}|galaxy\s+s2[2345]|galaxy\s+z|ipad)\b", q_norm):
        return 800.0
    if re.search(r"\b(galaxy|redmi\s+note|poco|smartphone|celular|moto\s+g|motorola\s+edge|nintendo\s+switch|ps4|playstation\s*4|notebook|laptop|smart\s+tv|geladeira|refrigerador|lava\s+e\s+seca|ar\s+condicionado|ar-condicionado)\b", q_norm):
        return 400.0
    if re.search(r"\b(monitor|tablet|air\s*fryer|fritadeira|micro-?ondas|aspirador\s+rob[oô]|rob[oô]\s+aspirador|airpods|kindle)\b", q_norm):
        return 180.0
    return 0.0

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
        "hardware",
        [
            r"\brtx\b", r"\brx \d{3,4}\b", r"\bplaca de v[ií]deo\b", r"\bryzen\b",
            r"\bintel core\b", r"\bssd\b", r"\bnvme\b", r"\bmem[oó]ria ram\b",
            r"\bplaca-m[aã]e\b", r"\bfonte \d+w\b", r"\bwater cooler\b", r"\bgabinete\b"
        ]
    ),
    (
        "perifericos",
        [
            r"\bmonitor\b", r"\bteclado\b", r"\bmouse\b", r"\bheadset\b",
            r"\bwebcam\b", r"\bmicrofone\b", r"\bmousepad\b", r"\bsuporte articulado\b"
        ]
    ),
    (
        "informatica",
        [
            r"\bnotebook\b", r"\blaptop\b", r"\bmacbook\b", r"\bcomputador\b",
            r"\btablet\b", r"\bipad\b", r"\broteador\b"
        ]
    ),
    (
        "eletronicos",
        [
            r"\bsmart tv\b", r"\btv \d{2}\b", r"\bfone de ouvido\b", r"\bheadphone\b",
            r"\bairpods\b", r"\bsoundbar\b", r"\bcaixa de som\b", r"\bjbl\b",
            r"\bprojetor\b", r"\bsmartwatch\b", r"\brel[oó]gio inteligente\b"
        ]
    ),
    (
        "games",
        [
            r"\bplaystation\b", r"\bps5\b", r"\bps4\b", r"\bxbox\b", r"\bnintendo switch\b",
            r"\bdualshock\b", r"\bdualsense\b", r"\bconsole\b", r"\bjogo ps\b",
            r"\bcontrole sem fio\b", r"\bgamer\b", r"\bvolante\b"
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
            r"\becho\b", r"\balexa\b", r"\bfechadura digital\b", r"\bl[aâ]mpada\b",
            r"\bjogo de panelas\b", r"\bpanela de press[aã]o\b", r"\bcolch[aã]o\b",
            r"\bcadeira ergon[oô]mica\b", r"\bcadeira gamer\b"
        ]
    ),
    (
        "esportes",
        [
            r"\bt[eê]nis\b", r"\bcorrida\b", r"\bacademia\b", r"\bcamisa de time\b",
            r"\bchuteira\b", r"\bmochila esportiva\b", r"\bgarmin\b"
        ]
    ),
    (
        "saude",
        [
            r"\bwhey\b", r"\bcreatina\b", r"\bsuplemento\b", r"\bpr[eé]-treino\b",
            r"\b[oô]mega 3\b", r"\bvitamina\b", r"\bbarra de prote[ií]na\b"
        ]
    ),
    (
        "ferramentas",
        [
            r"\bparafusadeira\b", r"\bfuradeira\b", r"\blavadora de alta press[aã]o\b",
            r"\bjogo de ferramentas\b", r"\btrena\b", r"\bserra\b", r"\bmaleta de ferramentas\b"
        ]
    ),
    (
        "livros",
        [
            r"\bkindle\b", r"\blivro\b", r"\bbox trilogia\b", r"\bcapa dura\b",
            # "manga" de roupa (manga curta/longa...) não é mangá (quadrinhos)
            r"\bhq\b", r"\bmang[aá]\b(?!\s+(?:curta|longa|3/4|comprida|princesa|sino|bufante|bal[aã]o|morcego|raglan|ciganinha|flare))"
        ]
    ),
]

BRANDS = [
    "Apple", "Samsung", "Xiaomi", "Motorola", "LG", "Sony", "Dell", "Lenovo",
    "Asus", "Acer", "HP", "JBL", "Logitech", "Razer", "Kingston", "Corsair",
    "Mondial", "Philco", "Britânia", "Electrolux", "Brastemp", "Consul",
    "Philips", "Walita", "TCL", "Positivo", "HyperX", "Anker", "Baseus",
    "Nike", "Adidas", "Asics", "Olympikus", "Growth", "Max Titanium", "Dux",
    "Bosch", "DeWalt", "Makita", "Kärcher", "WAP", "Tramontina", "Vonder", "Garmin"
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
    # Antes de classificar como smartphone/console/notebook pelo nome do aparelho citado,
    # verifica se o título é de um acessório/peça compatível ("cabo para iPhone", "capinha Galaxy", etc.)
    if is_accessory_title(text):
        return "perifericos"

    for cat, patterns in CATEGORY_RULES:
        for pat in patterns:
            if re.search(pat, text):
                return cat

    return hint or "geral"


_SEARCH_STOPWORDS = {
    "de", "da", "do", "dos", "das", "com", "para", "pra", "em", "no", "na",
    "o", "a", "os", "as", "e", "por", "ate", "até", "um", "uma",
}
_SEARCH_UNITS = {
    "polegadas", "polegada", "pol", "pols", "inches", "inch", "giga", "gigas",
}


def extract_search_tokens(query: str) -> List[str]:
    """Extrai tokens significativos de uma busca, separando números colados a letras."""
    if not query:
        return []
    q_norm = fold_text(query).strip()
    q_norm = q_norm.replace('"', " ").replace("'", " ")
    # Separa letras e números exceto sufixos conhecidos como ps5, ps4, s24, s23, g84, a55, m1, m2, m3
    raw_tokens = [t.strip() for t in re.split(r"[\s\-_/,]+", q_norm) if t.strip()]
    tokens: List[str] = []
    for t in raw_tokens:
        if t in _SEARCH_STOPWORDS or t in _SEARCH_UNITS or t.startswith("poleg"):
            continue
        # Se for ex: "128gb" -> mantém "128"
        m_cap = re.match(r"^(\d+)(gb|tb|mb|hz|w|pol)$", t)
        if m_cap:
            tokens.append(m_cap.group(1))
            continue
        tokens.append(t)
    return tokens or raw_tokens


def score_search_match(title: str, price: float, query: str) -> Optional[int]:
    """Avalia se um produto corresponde à busca e retorna um score de relevância (maior = mais relevante), ou None se não corresponder."""
    if not title or not query:
        return None

    title_lower = title.lower().strip()
    q_lower = query.lower().strip()
    wants_acc = query_wants_accessory(q_lower)

    if not wants_acc:
        if is_accessory_title(title_lower):
            return None
        min_price = min_plausible_device_price(q_lower)
        if min_price > 0 and (price or 0.0) < min_price:
            return None

    tokens = extract_search_tokens(q_lower)
    if not tokens:
        return None

    # Tokens já vêm sem acento; compara com o título também sem acento ("hermetico" acha "Hermético").
    title_lower = fold_text(title_lower)

    for t in tokens:
        if t.isdigit():
            # Números de modelo/geração/capacidade (ex: '15', '24', '128', '32') exigem fronteira de palavra
            pattern = rf"\b{re.escape(t)}(gb|tb|mb|pol|p|\"|\'|\b)"
            if not re.search(pattern, title_lower):
                return None
        else:
            if len(t) <= 3:
                if not re.search(rf"\b{re.escape(t)}\b", title_lower):
                    return None
            elif t not in title_lower:
                return None

    # Cálculo de relevância
    score = 60
    clean_phrase = " ".join(tokens)
    phrase_pos = title_lower.find(clean_phrase)
    if phrase_pos == 0 or title_lower.startswith(("apple " + clean_phrase, "samsung " + clean_phrase, "smartphone " + clean_phrase, "console " + clean_phrase)):
        score += 35
    elif 0 < phrase_pos <= 25:
        score += 25
    elif phrase_pos > 25:
        score += 10

    # Se o usuário buscou o modelo base (ex: "iphone 15") sem "pro"/"max"/"plus", prioriza o modelo exato antes das variantes
    for variant in ("pro", "max", "plus", "ultra", "fe", "lite", "mini", "slim"):
        if variant not in tokens and re.search(rf"\b{variant}\b", title_lower):
            score -= 8

    return max(score, 10)


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
    if category == "smartphones" and (is_accessory_title(title) or price < 350.0):
        category = "perifericos"
    brand = raw.get("brand") or detect_brand(title)
    
    # Gera link comissionado se não fornecido. O domínio do link manda: o nome da loja pode ter espaços
    # ("Mercado Livre") e não bater com a chave da rede ("mercadolivre"), deixando o link sem a tag.
    store_slug = detect_store_from_url(url)
    if store_slug == "outros":
        store_slug = source.lower()
    affiliate_url = raw.get("affiliate_url") or build_affiliate_url(url, store_slug=store_slug)

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
