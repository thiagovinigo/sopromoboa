import scrapers.shopee_feed_deals as deals


def listing(item_id, category="casa", discount=20.0):
    return {
        "id": f"shf_{item_id}", "title": f"Produto {item_id}", "price": 100.0 - discount, "list_price": 100.0,
        "category": category, "source": "Shopee",
    }


def feeds(monkeypatch, by_source):
    monkeypatch.setenv("SHOPEE_FEED_URLS", ",".join(by_source))
    monkeypatch.setattr(deals, "read_feed_listings", lambda source: list(by_source[source]))


def test_without_feed_urls_nothing_is_collected(monkeypatch):
    monkeypatch.delenv("SHOPEE_FEED_URLS", raising=False)

    assert deals.scrape_shopee_feed() == []


def test_two_feeds_are_merged_without_repeating_an_item(monkeypatch):
    feeds(monkeypatch, {
        "https://a.example/1": [listing(1), listing(2)],
        "https://b.example/2": [listing(2), listing(3)],
    })

    result = deals.scrape_shopee_feed()

    assert sorted(item["id"] for item in result) == ["shf_1", "shf_2", "shf_3"]


def test_the_total_cap_limits_the_result(monkeypatch):
    monkeypatch.setattr(deals, "TOTAL_CAP", 4)
    feeds(monkeypatch, {"https://a.example/1": [listing(i, category=f"c{i % 3}") for i in range(20)]})

    assert len(deals.scrape_shopee_feed()) == 4


def test_the_per_category_cap_keeps_one_category_from_taking_over(monkeypatch):
    monkeypatch.setattr(deals, "PER_CATEGORY_CAP", 2)
    feeds(monkeypatch, {"https://a.example/1": [listing(i, category="casa") for i in range(10)] + [listing(99, category="pets")]})

    result = deals.scrape_shopee_feed()

    assert sorted(item["category"] for item in result) == ["casa", "casa", "pets"]


def test_a_feed_that_fails_does_not_stop_the_others(monkeypatch):
    def reader(source):
        if source == "https://ruim.example/1":
            raise RuntimeError("feed fora do ar")
        return [listing(7)]

    monkeypatch.setenv("SHOPEE_FEED_URLS", "https://ruim.example/1,https://bom.example/2")
    monkeypatch.setattr(deals, "read_feed_listings", reader)

    assert [item["id"] for item in deals.scrape_shopee_feed()] == ["shf_7"]
