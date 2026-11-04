import pytest

import shopee_feed as sf

HEADER = (
    "image_link,itemid,price,global_category1,description,global_category2,global_item_attributes,"
    "item_rating,sale_price,global_catid2,discount_percentage,image_link_3,title,global_catid1,"
    "product_link,product_short link"
)


def make_row(**overrides):
    row = {
        "image_link": "https://cf.shopee.com.br/file/abc123",
        "itemid": "58213593522",
        "price": "62.9",
        "global_category1": "Women Shoes",
        "global_category2": "Others",
        "item_rating": "4.91",
        "sale_price": "52.9",
        "discount_percentage": "16",
        "title": "Mule Mocassim Feminina Com Corrente Chic",
        "product_link": "https://shopee.com.br/product/866764066/58213593522",
        "product_short link": "https://shope.ee/an_redir?origin_link=https%3A%2F%2Fshopee.com.br%2Fproduct%2F1&affiliate_id=1",
    }
    row.update(overrides)
    return row


def test_build_raw_listing_maps_fields_and_uses_the_feed_affiliate_link():
    raw = sf.build_raw_listing(make_row())

    assert raw["id"] == "shf_58213593522"
    assert raw["title"] == "Mule Mocassim Feminina Com Corrente Chic"
    assert raw["price"] == 52.9
    assert raw["list_price"] == 62.9
    assert raw["url"] == "https://shopee.com.br/product/866764066/58213593522"
    assert raw["affiliate_url"].startswith("https://shope.ee/")
    assert raw["image_url"] == "https://cf.shopee.com.br/file/abc123"
    assert raw["source"] == "Shopee"
    assert raw["rating"] == 4.91
    assert raw["category"] == "moda"


@pytest.mark.parametrize(
    "overrides",
    [
        {"sale_price": "62.9"},  # sem desconto
        {"sale_price": "9", "price": "12"},  # abaixo do preço mínimo
        {"sale_price": "5", "price": "40"},  # abaixo do preço mínimo
        {"sale_price": "10", "price": "100"},  # desconto acima do teto (90%)
        {"sale_price": "60", "price": "62"},  # desconto abaixo do mínimo
        {"item_rating": "3.2"},
        {"item_rating": ""},
        {"image_link": ""},
        {"title": "  "},
        {"product_link": "https://shopee.com.br/search?keyword=mule"},
        {"product_link": "https://outra-loja.com/product/1/2"},
        {"product_short link": ""},
        {"product_short link": "https://evil.example.com/an_redir"},
        {"itemid": ""},
    ],
)
def test_build_raw_listing_rejects_unusable_rows(overrides):
    assert sf.build_raw_listing(make_row(**overrides)) is None


def test_build_raw_listing_drops_medicines():
    assert sf.build_raw_listing(make_row(title="Dipirona 500mg 10 Comprimidos Genérico")) is None
    assert sf.build_raw_listing(make_row(title="Mule Mocassim Feminina Chic")) is not None


def test_collect_listings_dedupes_by_item_id():
    rows = [make_row(), make_row(title="Duplicado"), make_row(itemid="2", product_link="https://shopee.com.br/product/9/2")]

    listings = sf.collect_listings(rows)

    assert sorted(x["id"] for x in listings) == ["shf_2", "shf_58213593522"]


def test_parse_feed_text_handles_bom_and_quoted_multiline_descriptions():
    text = (
        "﻿" + HEADER + "\n"
        '"https://cf.shopee.com.br/file/a",1,62.9,Women Shoes,"linha 1\nlinha 2, com vírgula",Others,,4.9,52.9,1,16,,'
        "Mule Teste,2,https://shopee.com.br/product/5/1,https://shope.ee/an_redir?x=1\n"
    )

    rows = list(sf.parse_feed_text(text))

    assert len(rows) == 1
    assert rows[0]["itemid"] == "1"
    assert rows[0]["title"] == "Mule Teste"
    assert rows[0]["description"].startswith("linha 1")


def test_read_feed_text_reads_local_files(tmp_path):
    path = tmp_path / "feed.csv"
    path.write_text(HEADER + "\n", encoding="utf-8-sig")

    assert sf.read_feed_text(str(path)).startswith(HEADER)


def test_feed_sources_splits_the_environment_variable(monkeypatch):
    monkeypatch.setenv("SHOPEE_FEED_URLS", " https://a.example/1 , ,https://b.example/2 ")
    assert sf.feed_sources() == ["https://a.example/1", "https://b.example/2"]

    monkeypatch.delenv("SHOPEE_FEED_URLS")
    assert sf.feed_sources() == []


CSV_TEXT = (
    HEADER + "\n"
    '"https://cf.shopee.com.br/file/a",1,62.9,Women Shoes,"linha 1\nlinha 2, com vírgula",Others,,4.9,52.9,1,16,,'
    "Mule Açaí Teste,2,https://shopee.com.br/product/5/1,https://shope.ee/an_redir?x=1\n"
    '"https://cf.shopee.com.br/file/b",2,100,Home,"outra, descrição",Others,,4.8,80,1,20,,'
    "Panela Antiaderente,2,https://shopee.com.br/product/5/2,https://shope.ee/an_redir?x=2\n"
)


@pytest.mark.parametrize("chunk_size", [1, 2, 3, 7, 64, 100_000])
def test_streaming_reader_survives_chunk_cuts_inside_accents_and_quoted_newlines(chunk_size):
    data = ("﻿" + CSV_TEXT).encode("utf-8")
    chunks = [data[i:i + chunk_size] for i in range(0, len(data), chunk_size)]

    rows = list(sf.iter_csv_rows(chunks))

    assert [r["itemid"] for r in rows] == ["1", "2"]
    assert rows[0]["title"] == "Mule Açaí Teste"
    assert rows[0]["description"] == "linha 1\nlinha 2, com vírgula"


def test_iter_feed_rows_streams_an_https_feed_without_reading_it_all(monkeypatch):
    class Streamed:
        def raise_for_status(self):
            pass

        def iter_content(self, chunk_size=1):
            data = CSV_TEXT.encode("utf-8")
            yield from (data[i:i + 50] for i in range(0, len(data), 50))

        def close(self):
            pass

    monkeypatch.setattr(sf.requests, "get", lambda *args, **kwargs: Streamed())

    assert [r["itemid"] for r in sf.iter_feed_rows("https://feed.example/x")] == ["1", "2"]


def flaky_reader(monkeypatch, failures_before_success):
    """Feed que entrega uma linha boa, cai (ChunkedEncodingError) as primeiras vezes e depois entrega a segunda."""
    calls = {"n": 0}

    def reader(source):
        calls["n"] += 1
        yield make_row(itemid="1", product_link="https://shopee.com.br/product/5/1")
        if calls["n"] <= failures_before_success:
            raise sf.requests.exceptions.ChunkedEncodingError("conexão caiu no meio do arquivo")
        yield make_row(itemid="2", product_link="https://shopee.com.br/product/5/2")

    monkeypatch.setattr(sf, "iter_feed_rows", reader)
    return calls


def test_a_feed_that_drops_midway_is_read_again_until_it_works(monkeypatch):
    calls = flaky_reader(monkeypatch, failures_before_success=2)

    listings = sf.read_feed_listings("https://feed.example/x", sleep=lambda seconds: None)

    assert calls["n"] == 3
    assert sorted(l["id"] for l in listings) == ["shf_1", "shf_2"]


def test_when_every_attempt_fails_the_partial_read_is_kept(monkeypatch):
    calls = flaky_reader(monkeypatch, failures_before_success=99)

    listings = sf.read_feed_listings("https://feed.example/x", attempts=3, sleep=lambda seconds: None)

    assert calls["n"] == 3
    assert [l["id"] for l in listings] == ["shf_1"]


def test_an_error_that_is_not_a_network_failure_is_not_retried(monkeypatch):
    calls = {"n": 0}

    def reader(source):
        calls["n"] += 1
        yield make_row()
        raise ValueError("linha corrompida")

    monkeypatch.setattr(sf, "iter_feed_rows", reader)

    listings = sf.read_feed_listings("https://feed.example/x", sleep=lambda seconds: pytest.fail("não deveria esperar"))

    assert calls["n"] == 1
    assert len(listings) == 1


def test_the_wait_between_attempts_grows_and_is_not_applied_after_the_last_one(monkeypatch):
    flaky_reader(monkeypatch, failures_before_success=99)
    waits = []

    sf.read_feed_listings("https://feed.example/x", attempts=3, wait_seconds=10.0, sleep=waits.append)

    assert waits == [10.0, 20.0]


def test_a_local_feed_file_is_read_in_streaming_mode(tmp_path):
    path = tmp_path / "feed.csv"
    path.write_text(CSV_TEXT, encoding="utf-8")

    rows = list(sf.iter_feed_rows(str(path)))

    assert [r["itemid"] for r in rows] == ["1", "2"]
