import pytest

import lomadee_client as lc

BRAND_ID = "83245e45-1d3b-41d3-ad55-a718bae7792b"

BRAND = {
    "id": BRAND_ID,
    "name": "Manclub",
    "segment": "roupas",
    "commission": {"value": 7.2, "transfer": "cpa"},
    "network": {"active": True, "isPublic": True},
    "channels": [{"name": "Que Promo", "shortUrls": ["https://lmdee.link/abc"]}],
}


def make_product(**overrides):
    product = {
        "id": "prod-1",
        "organizationId": BRAND_ID,
        "name": "Cueca das Joias MANCLUB",
        "url": "https://manclub.com.br/cueca/p",
        "available": True,
        "images": [{"url": "https://img.example.com/cueca.png"}],
        "options": [{"available": True, "pricing": [{"price": 59, "listPrice": 99}]}],
    }
    product.update(overrides)
    return product


def test_build_raw_listing_maps_fields():
    raw = lc.build_raw_listing(make_product(), BRAND)

    assert raw["title"] == "Cueca das Joias MANCLUB"
    assert raw["price"] == 59.0
    assert raw["list_price"] == 99.0
    assert raw["source"] == "Manclub"
    assert raw["url"] == "https://manclub.com.br/cueca/p"
    assert raw["image_url"] == "https://img.example.com/cueca.png"
    assert raw["id"].startswith(lc.PRODUCT_ID_PREFIX)


def test_listing_id_is_stable_and_short():
    first = lc.build_raw_listing(make_product(), BRAND)["id"]
    second = lc.build_raw_listing(make_product(), BRAND)["id"]

    assert first == second
    assert len(first) == len(lc.PRODUCT_ID_PREFIX) + 12


@pytest.mark.parametrize(
    "overrides",
    [
        {"available": False},
        {"images": []},
        {"url": "http://insecure.example.com/p"},
        {"options": [{"available": True, "pricing": [{"price": 5, "listPrice": 10}]}]},
        {"options": [{"available": True, "pricing": [{"price": 99, "listPrice": 99}]}]},
        {"options": [{"available": True, "pricing": [{"price": 95, "listPrice": 100}]}]},
        {"options": [{"available": True, "pricing": [{"price": 20, "listPrice": 100}]}]},
        {"options": []},
    ],
)
def test_build_raw_listing_rejects_unusable_products(overrides):
    assert lc.build_raw_listing(make_product(**overrides), BRAND) is None


def test_build_raw_listing_rejects_inactive_brand():
    inactive = {**BRAND, "network": {"active": False}}

    assert lc.build_raw_listing(make_product(), inactive) is None


def test_select_listings_applies_per_brand_and_total_caps():
    listings = [
        {"id": f"a{i}", "source": "A", "price": 50.0, "list_price": 50.0 + i + 6}
        for i in range(5)
    ] + [
        {"id": f"b{i}", "source": "B", "price": 50.0, "list_price": 50.0 + i + 6}
        for i in range(5)
    ]

    per_brand = lc.select_listings(listings, per_brand_cap=2, total_cap=100)
    assert [x["source"] for x in per_brand].count("A") == 2
    assert [x["source"] for x in per_brand].count("B") == 2

    total = lc.select_listings(listings, per_brand_cap=5, total_cap=3)
    assert len(total) == 3


def test_select_listings_prefers_larger_discounts_within_a_brand():
    listings = [
        {"id": "small", "source": "A", "price": 90.0, "list_price": 100.0},
        {"id": "big", "source": "A", "price": 60.0, "list_price": 100.0},
    ]

    selected = lc.select_listings(listings, per_brand_cap=1, total_cap=10)

    assert [x["id"] for x in selected] == ["big"]


def test_pick_short_url_prefers_named_channel_and_skips_blocked():
    channels = [
        {"name": "Outro", "shortUrls": ["https://lmdee.link/outro"]},
        {"name": "Que Promo", "shortUrls": ["https://lmdee.link/qp"]},
        {"name": "Bloqueado", "shortUrls": [], "message": "sem permissão"},
    ]

    assert lc.pick_short_url(channels) == "https://lmdee.link/qp"
    assert lc.pick_short_url([channels[0]]) == "https://lmdee.link/outro"
    assert lc.pick_short_url([channels[2]]) is None
    assert lc.pick_short_url([]) is None


def test_is_short_link():
    assert lc.is_short_link("https://lmdee.link/abc")
    assert not lc.is_short_link("https://manclub.com.br/cueca/p")
    assert not lc.is_short_link(None)


def test_collect_listings_skips_unknown_brands():
    products = [make_product(), make_product(id="p2", organizationId="unknown-org")]
    brands = {BRAND_ID: BRAND}

    listings = lc.collect_listings(brands, products)

    assert len(listings) == 1
    assert listings[0]["source"] == "Manclub"


def test_get_api_key_reads_environment(monkeypatch):
    monkeypatch.setenv("LOMADEE_API_KEY", "  lmd_test_key  ")
    assert lc.get_api_key() == "lmd_test_key"

    monkeypatch.delenv("LOMADEE_API_KEY")
    assert lc.get_api_key() is None
