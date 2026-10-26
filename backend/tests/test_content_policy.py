import pytest

from content_policy import is_restricted_listing

PHARMACY = "Drogasmil Perfimaria e farmácia"


@pytest.mark.parametrize(
    "title,hint",
    [
        ("Hemifumarato de Bisoprolol 5mg Genérico Medley", PHARMACY),
        ("Cloridrato De Terbinafina 250mg 28 Comprimidos", PHARMACY),
        ("Dipirona Monoidratada 500 mg 10 Comprimidos", ""),
        ("Amoxicilina 500mg Cápsulas", ""),
        ("Xarope Expectorante Infantil 120ml", ""),
        ("Colírio Lubrificante 15ml", ""),
        ("Natus Gerin 50 Cápsulas", "PromoFarma remédios e cosméticos"),
        ("Paracetamol Gotas", ""),
        ("Anti-inflamatório Gel", ""),
    ],
)
def test_medicines_are_restricted(title, hint):
    assert is_restricted_listing(title, hint) is True


@pytest.mark.parametrize(
    "title,hint",
    [
        ("Protetor Solar Corporal Antiox Complex FPS 50", PHARMACY),
        ("Shampoo Anticaspa 400ml", PHARMACY),
        ("Perfume Feminino Floral 100ml", "PromoFarma remédios e cosméticos"),
        ("Fralda Descartável Tamanho M", PHARMACY),
        ("Creatina Monohidratada 300g", ""),
        ("Kit 6 Cápsulas de Café Compatível Nespresso", ""),
        ("Pijama Infantil Manga Curta", "UP Kids roupas infantis"),
        ("Whey Protein 900g Baunilha", ""),
    ],
)
def test_ordinary_products_pass(title, hint):
    assert is_restricted_listing(title, hint) is False


def test_pharmacy_items_outside_personal_care_are_restricted():
    assert is_restricted_listing("Produto Sem Descrição Clara 30 un", PHARMACY) is True
    assert is_restricted_listing("Produto Sem Descrição Clara 30 un", "Móveis Carraro") is False
