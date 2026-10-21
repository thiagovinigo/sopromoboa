"""Utilitários para extração e parsing de valores monetários no padrão brasileiro (R$)."""
import re
from typing import Optional

_PRICE_RE = re.compile(r"R\$\s*([0-9]{1,3}(?:\.[0-9]{3})*|\d+)(?:,([0-9]{2}))?", re.IGNORECASE)
_RAW_NUMBER_RE = re.compile(r"([0-9]+(?:\.[0-9]{3})*),([0-9]{2})")


def extract_price(text: Optional[str]) -> float:
    """Extrai valor numérico de strings contendo preços em Real (ex: 'R$ 1.499,90' -> 1499.90)."""
    if not text:
        return 0.0

    clean_text = text.replace("\xa0", " ").strip()

    # 1. Procura com R$
    match = _PRICE_RE.search(clean_text)
    if match:
        whole = match.group(1).replace(".", "")
        cents = match.group(2) or "00"
        try:
            return float(f"{whole}.{cents}")
        except ValueError:
            return 0.0

    # 2. Procura padrão '1.299,99'
    match_raw = _RAW_NUMBER_RE.search(clean_text)
    if match_raw:
        whole = match_raw.group(1).replace(".", "")
        cents = match_raw.group(2)
        try:
            return float(f"{whole}.{cents}")
        except ValueError:
            return 0.0

    # 3. Fallback para dígitos simples com ponto decimal americano
    match_fallback = re.search(r"\b\d+\.\d{2}\b", clean_text)
    if match_fallback:
        try:
            return float(match_fallback.group(0))
        except ValueError:
            return 0.0

    return 0.0


def extract_discount_badge(text: Optional[str]) -> float:
    """Extrai percentual de desconto indicado na página (ex: '35% OFF' -> 35.0)."""
    if not text:
        return 0.0
    match = re.search(r"(\d{1,2})\s*%\s*(?:off|desconto)", text, re.IGNORECASE)
    if match:
        try:
            return float(match.group(1))
        except ValueError:
            pass
    return 0.0
