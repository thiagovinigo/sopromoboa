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
