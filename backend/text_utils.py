"""Utilitários de texto compartilhados entre o banco e a busca."""
import unicodedata
from typing import Optional


def fold_text(value: Optional[str]) -> str:
    """Minúsculas e sem acentos: "Hermético" -> "hermetico". Usado para comparar busca e título."""
    if not value:
        return ""
    decomposed = unicodedata.normalize("NFKD", value.lower())
    return "".join(ch for ch in decomposed if not unicodedata.combining(ch))
