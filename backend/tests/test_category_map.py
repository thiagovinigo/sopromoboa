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
        ("Vestido Infantil Manga Curta em Laise", "UP Kids roupas infantis", "infantil"),
        ("Pijama Feminino Manga Longa", "Malwee Moda feminina", "moda"),
        ("Mangá One Piece Vol 1", "", "livros"),
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


def test_accessories_mentioning_phone_models_are_classified_as_perifericos():
    from normalize import detect_category, is_accessory_title, score_search_match

    assert is_accessory_title("Capinha Kuromi iPhone 15 14 13 12 11 16 17 Pro Max")
    assert is_accessory_title("Cabo Carregador Usb-c Tipo C Turbo 60w Para iPhone 15")
    assert is_accessory_title("Microfone Lapela Redondo Sem Fio Para Android E iPhone 15 16")
    assert not is_accessory_title("Apple iPhone 15 (128 GB) - Preto - Distribuidor Autorizado")

    assert detect_category("Capinha Kuromi iPhone 15 14 13") == "perifericos"
    assert detect_category("Cabo Carregador Usb-c Para iPhone 15") == "perifericos"
    assert detect_category("Apple iPhone 15 (128 GB) - Preto") == "smartphones"

    # Busca por "iphone 15" rejeita acessórios e aceita o aparelho real
    assert score_search_match("Capinha Kuromi iPhone 15 14 13", 15.99, "iphone 15") is None
    assert score_search_match("Cabo Carregador Usb-c Para iPhone 15", 19.79, "iphone 15") is None
    base_score = score_search_match("Apple iPhone 15 (128 GB) - Preto", 4299.0, "iphone 15")
    pro_score = score_search_match("Apple iPhone 15 Pro (128 GB) - Titânio", 5999.0, "iphone 15")
    assert base_score is not None and pro_score is not None
    assert base_score > pro_score

    # Mas se o usuário buscar explicitamente "cabo iphone 15", aceita o cabo
    assert score_search_match("Cabo Carregador Usb-c Para iPhone 15", 19.79, "cabo iphone 15") is not None


def test_every_returned_category_has_a_label():
    for slug in ("moda", "infantil", "beleza", "automotivo", "papelaria", "pets", "casa", "geral", "saude"):
        assert slug in CATEGORY_LABELS
