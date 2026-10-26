from affiliate import build_affiliate_url, detect_store_from_url, create_managed_link


def test_detect_store():
    assert detect_store_from_url("https://www.amazon.com.br/dp/B0CHX1W1XY") == "amazon"
    assert detect_store_from_url("https://www.mercadolivre.com.br/item/MLB123") == "mercadolivre"
    assert detect_store_from_url("https://www.magazineluiza.com.br/produto/p/123") == "magalu"
    assert detect_store_from_url("https://www.kabum.com.br/produto/123") == "kabum"


def test_build_amazon_affiliate_url():
    url = "https://www.amazon.com.br/dp/B0CHX1W1XY?ref=abc"
    tagged = build_affiliate_url(url, store_slug="amazon", custom_tag="minhatag-20")
    assert "tag=minhatag-20" in tagged
    assert "utm_source=sopromoboa" in tagged


def test_build_magalu_affiliate_url():
    url = "https://www.magazineluiza.com.br/produto/p/123"
    tagged = build_affiliate_url(url, store_slug="magalu", custom_tag="minhaloja")
    assert "parceiro=minhaloja" in tagged


def test_normalize_listing_tags_by_domain_even_when_the_store_name_has_spaces():
    from normalize import normalize_listing

    ml = normalize_listing({
        "id": "x1", "title": "Fone", "price": 100.0, "source": "Mercado Livre",
        "url": "https://produto.mercadolivre.com.br/MLB-123-fone",
    })
    amazon = normalize_listing({
        "id": "x2", "title": "Fone", "price": 100.0, "source": "Amazon",
        "url": "https://www.amazon.com.br/dp/B0CHX1W1XY",
    })
    other = normalize_listing({
        "id": "x3", "title": "Sofá", "price": 100.0, "source": "Sofá na Caixa",
        "url": "https://www.sofanacaixa.com.br/p/1",
    })

    assert "matt_tool=" in ml["affiliate_url"]
    assert "tag=" in amazon["affiliate_url"]
    assert "matt_tool=" not in other["affiliate_url"] and "tag=" not in other["affiliate_url"]


def test_create_managed_link():
    res = create_managed_link("https://www.amazon.com.br/dp/B0CHX1W1XY")
    assert res["store"] == "amazon"
    assert "tag=" in res["affiliate_url"]
