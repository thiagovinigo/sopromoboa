import pytest

from category_map import CATEGORY_LABELS, category_for


@pytest.mark.parametrize(
    "title,hint,expected",
    [
        ("Vestido Midi Floral", "Malwee Moda feminina", "moda"),
        ("Macacão Bebê Algodão", "UP Kids roupas infantis", "infantil"),
        ("Cama Montessoriana Solteiro", "LITTLE DUCK others", "infantil"),
        ("Mesa de Jantar 6 Cadeiras", "Móveis Carraro Sala de jantar, cozinhas", "casa"),
        ("Compressor Ar Condicionado", "Friopeças Ar Condicionado, Eletrodomésticos", "eletrodomesticos"),
        ("Placa de Vídeo RTX", "Shopinfo Pc gamer, Acessórios gamer e Hardware", "hardware"),
        ("Dipirona 500mg", "Drogasmil Perfimaria e farmácia", "saude"),
        ("Batom Matte", "Beauty Makeup", "beleza"),
        ("Capacete Moto Fechado", "Moto BR outros", "automotivo"),
        ("Caderno Universitário", "Stationery Notebooks", "papelaria"),
        ("Coleira para Cachorro", "Pet Supplies", "pets"),
        ("Guarda-roupa 6 Portas", "Móveis Carraro guarda roupas", "casa"),
        ("Camisa Masculina Slim Homem", "", "moda"),
        ("Isotônico Limão 500ml", "Gatorade", "geral"),
        ("Produto qualquer sem pista", "", "geral"),
    ],
)
def test_category_for_uses_title_then_hint(title, hint, expected):
    assert category_for(title, hint) == expected


def test_title_rules_from_normalize_win_over_the_hint():
    # "iphone" é classificado como smartphones pelas regras por título, independentemente da dica
    assert category_for("iPhone 15 128GB", "Loja de roupas moda") == "smartphones"


def test_every_returned_category_has_a_label():
    for slug in ("moda", "infantil", "beleza", "automotivo", "papelaria", "pets", "casa", "geral", "saude"):
        assert slug in CATEGORY_LABELS
