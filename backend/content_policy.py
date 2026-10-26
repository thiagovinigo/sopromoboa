"""Política de conteúdo do catálogo: produtos que não devem ser divulgados ao público.

No Brasil a propaganda de medicamentos (principalmente os de tarja) ao público é restrita pela Anvisa
(RDC 96/2008) e pelas políticas do Google AdSense. A regra é conservadora: na dúvida, o item não entra.
"""
import re

# Termos que identificam medicamento por si só.
_MEDICINE_RE = re.compile(
    r"gen[eé]rico|medicamento|\bbula\b|\btarja\b|\bmcg\b|\b\d+\s?mg\b|\bxarope\b|\bampolas?\b|injet[aá]vel"
    r"|solu[cç][aã]o oral|col[ií]rio|antibi[oó]tic|anti-?inflamat|analg[eé]sic|\bdipirona\b|\bparacetamol\b"
    r"|\bibuprofeno\b|\bomeprazol\b|\bamoxicilina\b|\bdiclofenaco\b|\bgotas\b",
    re.IGNORECASE,
)

# Termos fracos: só contam quando a loja é uma farmácia (em outras lojas "cápsulas" é café, creatina etc.).
_WEAK_MEDICINE_RE = re.compile(r"comprimidos?|c[aá]psulas?|\bpomada\b|\bsach[eê]s?\b", re.IGNORECASE)

_PHARMACY_STORE_RE = re.compile(r"farm[aá]cia|drogaria|drogas|rem[eé]dio|promofarma", re.IGNORECASE)

# Em farmácias só entram itens de perfumaria, higiene e cuidados pessoais.
_PERSONAL_CARE_RE = re.compile(
    r"shampoo|condicionador|sabonete|desodorante|protetor solar|filtro solar|hidratante|\bcreme\b|lo[cç][aã]o"
    r"|perfume|col[oô]nia|maquiagem|batom|esmalte|escova|fio dental|enxaguante|fralda|absorvente|barbe|l[aâ]mina"
    r"|cotonete|s[eé]rum|m[aá]scara|repelente|pente|secador|prancha|cosm[eé]tic",
    re.IGNORECASE,
)


def is_restricted_listing(title: str, store_hint: str = "") -> bool:
    """True se o item parece medicamento ou, numa farmácia, não é de perfumaria/higiene."""
    text = title or ""
    if _MEDICINE_RE.search(text):
        return True
    if _PHARMACY_STORE_RE.search(store_hint or ""):
        return bool(_WEAK_MEDICINE_RE.search(text)) or not _PERSONAL_CARE_RE.search(text)
    return False
