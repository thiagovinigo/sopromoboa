"""Classificação de categorias para ofertas que chegam com pistas em texto livre (segmento da loja, categoria do feed).

Primeiro valem as regras por título de normalize.detect_category; sem acerto, usa a dica da loja/feed.
"""
import re
from typing import List, Tuple

from normalize import detect_category

CATEGORY_LABELS = {
    "smartphones": "Smartphones & Celulares",
    "informatica": "Informática & Notebooks",
    "hardware": "Hardware & Peças PC",
    "perifericos": "Periféricos & Acessórios",
    "eletronicos": "Eletrônicos, Áudio & TV",
    "games": "Games & Consoles",
    "eletrodomesticos": "Eletrodomésticos & Cozinha",
    "casa": "Casa, Móveis & Decoração",
    "esportes": "Esportes & Calçados",
    "saude": "Saúde & Suplementos",
    "ferramentas": "Ferramentas & Jardim",
    "livros": "Livros & E-readers",
    "moda": "Moda & Acessórios",
    "infantil": "Infantil & Bebê",
    "beleza": "Beleza & Perfumaria",
    "automotivo": "Automotivo & Motos",
    "papelaria": "Papelaria & Escritório",
    "pets": "Pets",
    "geral": "Geral & Outros",
}

# A ordem importa: a primeira regra que casar com a dica define a categoria.
_HINT_RULES: List[Tuple[str, "re.Pattern[str]"]] = [
    ("infantil", re.compile(r"infantil|beb[eê]|baby|kids|crian[cç]|brinqued|toy|montessori")),
    ("pets", re.compile(r"\bpets?\b|animal|cachorro|\bgatos?\b|\bc[aã]es\b")),
    ("automotivo", re.compile(r"vehicle|ve[ií]culo|automotiv|autom[oó]vel|\bmotos?\b|capacete|pneu")),
    ("papelaria", re.compile(r"stationery|papelaria|escrit[oó]rio|caderno")),
    ("hardware", re.compile(r"hardware|pc gamer|gamer")),
    ("eletrodomesticos", re.compile(r"eletrodom|ar condicionado|friope|climatiza")),
    ("saude", re.compile(r"farm[aá]cia|drogaria|drogas|sa[uú]de|health|suplement|rem[eé]dio")),
    ("beleza", re.compile(r"beleza|beauty|perfum|perfim|cosm[eé]tic|skin|maquiagem|makeup")),
    ("casa", re.compile(r"\bhome\b|living|m[oó]vel|m[oó]veis|sof[aá]|cozinha|\bsala\b|jantar|guarda.?roupa|decora|bedding|colch|jardim|garden|furniture|\bcama\b")),
    ("moda", re.compile(r"roupa|\bmoda\b|vestu|jeans|cal[cç]a|camis|sapato|bolsa|fashion|clothes|shoes|lingerie|underwear|moletom")),
    ("esportes", re.compile(r"sport|outdoor|esport|fitness|academia")),
    ("livros", re.compile(r"\bbooks?\b|livro|livraria")),
    ("smartphones", re.compile(r"mobile|gadget|celular|smartphone")),
    ("eletronicos", re.compile(r"electronic|eletr[oô]nic|[aá]udio|\btv\b")),
]


def category_for(title: str, hint: str = "") -> str:
    """Categoria por título (regras existentes) e, se vier 'geral', pela dica de loja/feed."""
    by_title = detect_category(title)
    if by_title != "geral":
        return by_title

    text = f"{hint or ''} {title or ''}".lower()
    for slug, pattern in _HINT_RULES:
        if pattern.search(text):
            return slug
    return "geral"
