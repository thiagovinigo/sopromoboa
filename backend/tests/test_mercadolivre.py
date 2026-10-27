import mercadolivre_client as ml

PRODUCT = {
    "id": "MLB45862017",
    "name": "Fone de Ouvido Bluetooth JBL Tune 520BT",
    "status": "active",
    "pictures": [{"url": "https://http2.mlstatic.com/D_NQ_NP_1-F.jpg"}],
}


def make_offer(**overrides):
    offer = {
        "item_id": "MLB5461607985",
        "price": 199.9,
        "original_price": 299.9,
        "condition": "new",
        "shipping": {"free_shipping": True},
    }
    offer.update(overrides)
    return offer


def test_item_url_points_to_the_item_page():
    assert ml.item_url("MLB5461607985") == "https://produto.mercadolivre.com.br/MLB-5461607985"


def test_pick_best_offer_takes_cheapest_new_offer():
    offers = [
        make_offer(item_id="MLB1", price=150.0, condition="used"),
        make_offer(item_id="MLB2", price=210.0),
        make_offer(item_id="MLB3", price=199.9),
    ]

    assert ml.pick_best_offer(offers)["item_id"] == "MLB3"


def test_pick_best_offer_ignores_offers_without_a_valid_price():
    offers = [make_offer(price=0), make_offer(price=None), make_offer(price="abc")]

    assert ml.pick_best_offer(offers) is None


def test_build_raw_listing_maps_fields():
    raw = ml.build_raw_listing(PRODUCT, make_offer(), "Eletrônicos, Áudio e Vídeo")

    assert raw["id"] == "mlp_MLB5461607985"
    assert raw["title"] == "Fone de Ouvido Bluetooth JBL Tune 520BT"
    assert raw["price"] == 199.9
    assert raw["list_price"] == 299.9
    assert raw["url"] == "https://produto.mercadolivre.com.br/MLB-5461607985"
    assert raw["source"] == "Mercado Livre"
    assert raw["image_url"] == "https://http2.mlstatic.com/D_NQ_NP_1-F.jpg"
    assert raw["free_shipping"] == 1


def test_build_raw_listing_never_invents_a_list_price():
    raw = ml.build_raw_listing(PRODUCT, make_offer(original_price=None), "Games")

    assert raw["list_price"] is None


def test_build_raw_listing_drops_implausible_list_price_but_keeps_item():
    # 90% "de desconto" é preço de lista inflado: o item entra sem desconto
    raw = ml.build_raw_listing(PRODUCT, make_offer(price=30.0, original_price=300.0), "Games")

    assert raw is not None
    assert raw["list_price"] is None


def test_build_raw_listing_drops_list_price_equal_or_below_price():
    raw = ml.build_raw_listing(PRODUCT, make_offer(original_price=199.9), "Games")

    assert raw["list_price"] is None


def test_build_raw_listing_rejects_unusable_products():
    assert ml.build_raw_listing({**PRODUCT, "status": "inactive"}, make_offer(), "Games") is None
    assert ml.build_raw_listing({**PRODUCT, "pictures": []}, make_offer(), "Games") is None
    assert ml.build_raw_listing({**PRODUCT, "name": " "}, make_offer(), "Games") is None
    assert ml.build_raw_listing(PRODUCT, make_offer(price=5.0, original_price=None), "Games") is None
    assert ml.build_raw_listing(PRODUCT, make_offer(price=90_000.0, original_price=None), "Games") is None
    assert ml.build_raw_listing(PRODUCT, make_offer(item_id=""), "Games") is None


def test_build_raw_listing_rejects_restricted_items():
    medicine = {**PRODUCT, "name": "Dipirona Monoidratada 500mg 20 comprimidos"}

    assert ml.build_raw_listing(medicine, make_offer(), "Saúde") is None


class FakeResponse:
    def __init__(self, status_code=200, payload=None):
        self.status_code = status_code
        self._payload = payload if payload is not None else {}
        self.headers = {}

    def json(self):
        return self._payload

    def raise_for_status(self):
        if self.status_code >= 400:
            raise ml.requests.HTTPError(str(self.status_code))


def make_client(monkeypatch, responses):
    """Cliente com token falso; `responses` é consumido na ordem a cada GET (exceções são levantadas)."""
    monkeypatch.setattr(ml, "fetch_token", lambda app_id, secret: "token")
    monkeypatch.setattr(ml, "MIN_REQUEST_INTERVAL_SECONDS", 0)
    monkeypatch.setattr(ml.time, "sleep", lambda seconds: None)
    queue = list(responses)

    def fake_get(url, **kwargs):
        item = queue.pop(0)
        if isinstance(item, Exception):
            raise item
        return item

    monkeypatch.setattr(ml.requests, "get", fake_get)
    return ml.MercadoLivreClient("id", "secret")


def test_client_retries_after_a_dropped_connection(monkeypatch):
    client = make_client(monkeypatch, [ml.requests.ConnectionError("reset"), FakeResponse(200, {"ok": 1})])

    assert client.get("/x") == {"ok": 1}


def test_client_returns_none_for_forbidden_or_missing_resources(monkeypatch):
    client = make_client(monkeypatch, [FakeResponse(403), FakeResponse(404)])

    assert client.get("/a") is None
    assert client.get("/b") is None


def test_client_gives_up_after_repeated_network_failures(monkeypatch):
    errors = [ml.requests.ConnectionError("reset")] * (ml.MAX_RETRIES + 1)
    client = make_client(monkeypatch, errors)

    try:
        client.get("/x")
    except ml.requests.ConnectionError:
        return
    raise AssertionError("esperava ConnectionError após esgotar as tentativas")


def test_collect_product_refs_dedupes_and_keeps_only_products():
    highlights = [
        ("Games", {"content": [
            {"id": "MLB1", "type": "PRODUCT"},
            {"id": "MLB9", "type": "ITEM"},
            {"id": "MLB2", "type": "PRODUCT"},
        ]}),
        ("Informática", {"content": [{"id": "MLB1", "type": "PRODUCT"}, {"id": "MLB3", "type": "PRODUCT"}]}),
    ]

    refs = ml.collect_product_refs(highlights)

    assert refs == [("MLB1", "Games"), ("MLB2", "Games"), ("MLB3", "Informática")]
