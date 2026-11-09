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
    assert "utm_source=quepromo" in tagged


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


def test_awin_link_is_applied_only_to_approved_stores():
    lauri = build_affiliate_url("https://www.lauriesporte.com.br/halter-10kg", utm_source="quepromo")
    assert "awin1.com/cread.php" in lauri
    assert "awinmid=118977" in lauri
    assert "awinaffid=3144638" in lauri
    assert "clickref=quepromo" in lauri

    pending = build_affiliate_url("https://www.centauro.com.br/bermuda-termica-nike-999.html", utm_source="quepromo")
    assert "awin1.com" not in pending
    assert pending.startswith("https://www.centauro.com.br/bermuda-termica-nike-999.html")


def test_awin_approval_can_be_enabled_by_env(monkeypatch):
    monkeypatch.setenv("AWIN_APPROVED", "centauro, nike")
    tagged = build_affiliate_url("https://www.nike.com.br/tenis-air-max", utm_source="quepromo")
    assert "awinmid=17652" in tagged
    centauro = build_affiliate_url("https://www.centauro.com.br/bermuda-999.html", utm_source="quepromo")
    assert "awinmid=17806" in centauro


def test_awin_mid_can_be_overridden_by_env(monkeypatch):
    monkeypatch.setenv("AWIN_APPROVED", "nike")
    monkeypatch.setenv("AWIN_MID_NIKE", "99999")
    tagged = build_affiliate_url("https://www.nike.com.br/tenis-air-max", utm_source="quepromo")
    assert "awinmid=99999" in tagged


def test_awin_stores_are_split_by_site():
    from affiliate import awin_stores_for_site, AWIN_STORES

    quepromo = set(awin_stores_for_site("quepromo"))
    mercagym = set(awin_stores_for_site("mercagym"))
    assert "electrolux" in quepromo and "electrolux" not in mercagym
    assert {"centauro", "nike", "adidas", "decathlon", "asics"} <= quepromo & mercagym
    assert {"lauriesporte", "puma", "underarmour", "mizuno", "olympikus", "dafiti"} <= mercagym - quepromo
    assert not ({"netshoes", "drogasil", "fastshop"} & set(AWIN_STORES))
    assert all(cfg["status"] in {"approved", "pending", "not_requested"} for cfg in AWIN_STORES.values())


def test_awin_detection_respects_domain_boundaries():
    assert detect_store_from_url("https://www.asics.com.br/tenis") == "asics"
    assert detect_store_from_url("https://loja.technos.com.br/relogio") == "technos"
    assert detect_store_from_url("https://basics.com.br/x") == "outros"
    assert detect_store_from_url("https://puma.com.evil.com/x") == "outros"
    assert detect_store_from_url("https://evil.com@puma.com/x") == "puma"  # hostname real é puma.com
    assert detect_store_from_url("https://www.amazon.com.br/dp/B1?x=nike.com.br") == "amazon"


def test_awin_link_escapes_params_and_ignores_foreign_custom_tag(monkeypatch):
    monkeypatch.setenv("AWIN_APPROVED", "centauro")
    url = build_affiliate_url(
        "https://www.centauro.com.br/p", store_slug="centauro", custom_tag="1&ued=https://evil.com#",
        utm_source="a&b=c",
    )
    assert "awinmid=17806" in url
    assert "evil.com" not in url
    assert "clickref=a%26b%3Dc" in url
    assert url.count("ued=") == 1


def test_awin_link_refuses_non_http_destinations(monkeypatch):
    from affiliate import build_awin_url
    import pytest

    with pytest.raises(ValueError):
        build_awin_url("javascript:alert(1)//lauriesporte.com.br", merchant_id="118977")
    monkeypatch.setenv("AWIN_APPROVED", "lauriesporte")
    assert "awin1.com" not in build_affiliate_url("javascript:alert(1)//x", store_slug="lauriesporte")
