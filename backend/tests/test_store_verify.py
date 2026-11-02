import json

import store_verify as sv

PRODUCT_URL = "https://www.loja.com.br/camisa-azul/p"


def vtex_payload(*offers):
    sellers = [
        {"commertialOffer": {"Price": price, "ListPrice": list_price, "AvailableQuantity": qty}}
        for price, list_price, qty in offers
    ]
    return json.dumps([{"items": [{"sellers": sellers}]}])


def ld_json_page(price, availability="https://schema.org/InStock"):
    data = {"@type": "Product", "offers": {"@type": "Offer", "price": price, "availability": availability}}
    return f'<html><script type="application/ld+json">{json.dumps(data)}</script></html>'


def make_raw(**overrides):
    raw = {"id": "lmd_1", "title": "Camisa", "price": 50.0, "list_price": 100.0, "url": PRODUCT_URL}
    raw.update(overrides)
    return raw


def fake_fetch(responses):
    def fetch(url):
        return responses.get(url, (404, ""))
    return fetch


def test_vtex_api_url_uses_the_product_slug():
    assert sv.vtex_api_url(PRODUCT_URL) == (
        "https://www.loja.com.br/api/catalog_system/pub/products/search/camisa-azul/p"
    )


def test_vtex_api_url_ignores_the_query_string():
    url = "https://www.loja.com.br/livro-x/p?idsku=12"
    assert sv.vtex_api_url(url).endswith("/search/livro-x/p")


def test_check_listing_uses_the_cheapest_in_stock_offer():
    api = sv.vtex_api_url(PRODUCT_URL)
    fetch = fake_fetch({api: (200, vtex_payload((70.0, 120.0, 0), (80.0, 120.0, 5), (90.0, 120.0, 2)))})

    verdict, offer = sv.check_listing(make_raw(), fetch)

    assert verdict == sv.OK
    assert offer.price == 80.0
    assert offer.list_price == 120.0


def test_check_listing_is_gone_when_nothing_is_in_stock():
    api = sv.vtex_api_url(PRODUCT_URL)
    fetch = fake_fetch({api: (200, vtex_payload((70.0, 120.0, 0)))})

    assert sv.check_listing(make_raw(), fetch) == (sv.GONE, None)


def test_check_listing_falls_back_to_json_ld_when_the_store_has_no_vtex_api():
    fetch = fake_fetch({PRODUCT_URL: (200, ld_json_page("27.99"))})

    verdict, offer = sv.check_listing(make_raw(), fetch)

    assert verdict == sv.OK
    assert offer.price == 27.99
    assert offer.list_price is None


def test_check_listing_is_gone_when_the_page_returns_404():
    assert sv.check_listing(make_raw(), fake_fetch({})) == (sv.GONE, None)


def test_check_listing_is_gone_when_json_ld_says_out_of_stock():
    page = ld_json_page("27.99", "https://schema.org/OutOfStock")

    assert sv.check_listing(make_raw(), fake_fetch({PRODUCT_URL: (200, page)})) == (sv.GONE, None)


def test_check_listing_is_unknown_when_rate_limited():
    api = sv.vtex_api_url(PRODUCT_URL)
    fetch = fake_fetch({api: (429, ""), PRODUCT_URL: (429, "")})

    assert sv.check_listing(make_raw(), fetch) == (sv.UNKNOWN, None)


def test_check_listing_is_unknown_when_the_page_has_no_readable_price():
    fetch = fake_fetch({PRODUCT_URL: (200, "<html>sem preco</html>")})

    assert sv.check_listing(make_raw(), fetch) == (sv.UNKNOWN, None)


def test_verify_listings_replaces_the_feed_price_with_the_live_one():
    api = sv.vtex_api_url(PRODUCT_URL)
    raws = [make_raw()]
    fetch = fake_fetch({api: (200, vtex_payload((80.0, 120.0, 3)))})

    result = sv.verify_listings(raws, fetch, workers=1)

    assert result[0]["price"] == 80.0
    assert result[0]["list_price"] == 120.0
    assert raws[0]["price"] == 50.0  # entrada não é mutada


def test_verify_listings_drops_a_fake_discount_when_the_store_shows_no_list_price():
    api = sv.vtex_api_url(PRODUCT_URL)
    fetch = fake_fetch({api: (200, vtex_payload((80.0, 80.0, 3)))})

    result = sv.verify_listings([make_raw()], fetch, workers=1)

    assert result[0]["price"] == 80.0
    assert result[0]["list_price"] is None


def test_verify_listings_drops_gone_and_unknown_items():
    ok_url = "https://www.loja.com.br/ok/p"
    ok2_url = "https://www.loja.com.br/ok2/p"
    unknown_url = "https://www.loja.com.br/limitado/p"
    raws = [
        make_raw(id="a", url=ok_url),
        make_raw(id="b", url="https://www.loja.com.br/sumiu/p"),
        make_raw(id="c", url=unknown_url),
        make_raw(id="d", url=ok2_url),
    ]
    fetch = fake_fetch({
        sv.vtex_api_url(ok_url): (200, vtex_payload((60.0, 100.0, 1))),
        sv.vtex_api_url(ok2_url): (200, vtex_payload((61.0, 100.0, 1))),
        sv.vtex_api_url(unknown_url): (429, ""),
        unknown_url: (429, ""),
    })

    result = sv.verify_listings(raws, fetch, workers=1)

    assert [r["id"] for r in result] == ["a", "d"]


def test_verify_listings_returns_nothing_during_an_outage():
    raws = [make_raw(id=str(i), url=f"https://www.loja.com.br/p{i}/p") for i in range(10)]

    assert sv.verify_listings(raws, lambda url: (0, ""), workers=1) == []


def test_redirect_away_from_the_product_page_counts_as_gone():
    assert sv.is_redirected_away("https://www.loja.com.br/camisa/p", "https://www.loja.com.br/") is True
    assert sv.is_redirected_away("https://www.loja.com.br/camisa/p", "https://www.loja.com.br/roupas") is True


def test_same_page_or_renamed_product_page_is_not_redirected_away():
    assert sv.is_redirected_away("https://www.loja.com.br/camisa/p", "https://www.loja.com.br/camisa/p") is False
    assert sv.is_redirected_away("https://loja.com.br/camisa/p", "https://www.loja.com.br/camisa/p") is False
    assert sv.is_redirected_away("https://www.loja.com.br/camisa/p", "https://www.loja.com.br/camisa-nova/p") is False


def test_verify_listings_drops_offers_whose_image_is_gone():
    good_url, bad_url, flaky_url = (f"https://www.loja.com.br/{n}/p" for n in ("bom", "ruim", "oscila"))
    raws = [
        make_raw(id="bom", url=good_url, image_url="https://cdn/bom.jpg"),
        make_raw(id="ruim", url=bad_url, image_url="https://cdn/ruim.jpg"),
        make_raw(id="oscila", url=flaky_url, image_url="https://cdn/oscila.jpg"),
    ]
    fetch = fake_fetch({sv.vtex_api_url(u): (200, vtex_payload((60.0, 100.0, 1))) for u in (good_url, bad_url, flaky_url)})
    statuses = {"https://cdn/bom.jpg": 200, "https://cdn/ruim.jpg": 404, "https://cdn/oscila.jpg": 0}

    result = sv.verify_listings(raws, fetch, workers=1, image_status=lambda url: statuses[url])

    assert [r["id"] for r in result] == ["bom", "oscila"]
