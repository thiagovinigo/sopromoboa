import gzip

import pytest

from scrapers import awin_feed as af


def row(**overrides):
    values = {
        "aw_product_id": "9001", "product_name": "Tênis Nike Pegasus 40 Masculino",
        "merchant_deep_link": "https://www.nike.com.br/tenis-pegasus-40/p?cor=preto",
        "merchant_image_url": "https://static.nike.com.br/1.jpg", "search_price": "499.99",
        "product_price_old": "699.99  BRL", "in_stock": "1", "brand_name": "Nike",
    }
    values.update(overrides)
    return values


def test_shoes_are_kept_because_quepromo_takes_everything():
    listing = af.build_raw_listing(row())

    assert listing["id"].startswith("awinnike_")
    assert listing["source"] == "Nike Brasil" and listing["brand"] == "Nike"
    assert listing["price"] == 499.99 and listing["list_price"] == 699.99
    assert listing["url"] == "https://www.nike.com.br/tenis-pegasus-40/p?cor=preto"
    assert listing["image_url"] == "https://static.nike.com.br/1.jpg"


def test_brand_store_items_are_always_sports_never_guessed_from_the_title():
    # "adidas Mouse Pad" ou "Livro" no título não podem mandar um tênis para periféricos ou livros
    assert af.build_raw_listing(row(product_name="Mochila adidas Mouse Pad Livro"))["category"] == "esportes"


def test_listing_leaves_the_affiliate_link_to_the_normalizer():
    assert "affiliate_url" not in af.build_raw_listing(row())


def test_store_not_approved_is_ignored():
    assert af.build_raw_listing(row(merchant_deep_link="https://www.centauro.com.br/tenis/p")) is None


def test_store_that_does_not_serve_quepromo_is_ignored_even_if_approved(monkeypatch):
    monkeypatch.setenv("AWIN_APPROVED", "puma")  # PUMA só atende o MercaGym
    assert af.build_raw_listing(row(merchant_deep_link="https://puma.com/br/pt/tenis-x")) is None


def test_product_without_stock_price_or_image_is_ignored():
    assert af.build_raw_listing(row(in_stock="0")) is None
    assert af.build_raw_listing(row(search_price="")) is None
    assert af.build_raw_listing(row(merchant_image_url="")) is None


def test_nike_feed_uses_stock_status_column():
    assert af.build_raw_listing(row(in_stock="", stock_status="in stock")) is not None
    assert af.build_raw_listing(row(in_stock="", stock_status="out of stock")) is None
    assert af.build_raw_listing({k: v for k, v in row().items() if k != "in_stock"}) is None


def test_http_link_is_upgraded_and_old_price_suffix_is_ignored():
    listing = af.build_raw_listing(row(merchant_deep_link="http://www.adidas.com.br/tenis/JI4235.html",
                                       product_price_old="799.99  BRL"))
    assert listing["url"] == "https://www.adidas.com.br/tenis/JI4235.html"
    assert listing["list_price"] == 799.99


def test_list_price_not_above_sale_price_is_dropped():
    assert af.build_raw_listing(row(product_price_old="400.00"))["list_price"] is None


def test_size_variants_of_the_same_page_collapse_into_one_listing():
    base = "https://www.nike.com.br/tenis/JI4235.html"
    rows = [row(aw_product_id=str(n), merchant_deep_link=f"{base}?size={n}") for n in (1, 2, 3)]

    assert len(af.collect_listings(rows, "nike")) == 1


def test_listing_id_is_stable_between_runs():
    assert af.build_raw_listing(row())["id"] == af.build_raw_listing(row())["id"]


def test_only_listings_of_the_requested_store_are_collected():
    rows = [row(), row(aw_product_id="2", merchant_deep_link="https://www.adidas.com.br/tenis-a/A1.html")]

    assert [l["source"] for l in af.collect_listings(rows, "adidas")] == ["adidas Brasil"]
    assert [l["source"] for l in af.collect_listings(rows, "nike")] == ["Nike Brasil"]


def test_gzip_feed_is_decompressed_in_streamed_chunks():
    csv_text = "aw_product_id,product_name\n1,Tenis A\n2,Camiseta B\n"
    data = gzip.compress(csv_text.encode("utf-8"))
    chunks = [data[i:i + 7] for i in range(0, len(data), 7)]

    assert [r["aw_product_id"] for r in af.iter_csv_rows(chunks)] == ["1", "2"]
    plain = [csv_text.encode("utf-8")[:20], csv_text.encode("utf-8")[20:]]
    assert [r["aw_product_id"] for r in af.iter_csv_rows(plain)] == ["1", "2"]


def test_scrapers_without_configured_feed_return_nothing(monkeypatch):
    monkeypatch.delenv("AWIN_FEED_URL_NIKE", raising=False)
    monkeypatch.delenv("AWIN_FEED_URL_ADIDAS", raising=False)
    assert af.scrape_awin_nike() == []
    assert af.scrape_awin_adidas() == []


def test_feed_read_from_a_local_file_end_to_end(tmp_path, monkeypatch):
    header = "aw_product_id,product_name,merchant_deep_link,merchant_image_url,search_price,in_stock,brand_name\n"
    lines = ("1,Camiseta Nike Club,https://www.nike.com.br/camiseta-club/p,https://img/1.jpg,99.90,1,Nike\n"
             "2,Tenis Nike Air,https://www.nike.com.br/tenis-air/p,https://img/2.jpg,399.90,1,Nike\n")
    feed = tmp_path / "nike.csv.gz"
    feed.write_bytes(gzip.compress((header + lines).encode("utf-8")))
    monkeypatch.setenv("AWIN_FEED_URL_NIKE", str(feed))

    listings = af.scrape_awin_nike()

    assert sorted(l["title"] for l in listings) == ["Camiseta Nike Club", "Tenis Nike Air"]


def test_normalizer_turns_the_feed_listing_into_an_awin_link():
    from normalize import normalize_listing

    normalized = normalize_listing(af.build_raw_listing(row()))

    assert "awinmid=17652" in normalized["affiliate_url"]
    assert "clickref=quepromo" in normalized["affiliate_url"]
    assert normalized["source"] == "Nike Brasil"


@pytest.mark.parametrize("slug", ["nike", "adidas"])
def test_both_stores_are_approved_for_quepromo(slug):
    from affiliate import awin_is_approved, awin_stores_for_site

    assert awin_is_approved(slug) and slug in awin_stores_for_site("quepromo")
