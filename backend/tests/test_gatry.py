from datetime import datetime, timedelta

import pytest
from bs4 import BeautifulSoup

from scrapers import gatry_deals as gd

NOW = datetime(2026, 10, 26, 20, 0, 0)  # UTC


def make_card(
    title="WAP Parafusadeira Impacto 3/8 700W",
    price="R$ 96,52",
    store="Amazon",
    href="https://www.amazon.com.br/WAP/dp/B0F678PCRM?tag=gatry0b-20&",
    posted="26/10/2026 às 13:05",
    image="https://cdn.gatry.com/img/a.jpg",
):
    html = f"""
    <article>
      <div class="image"><a href="{href}"><img src="{image}" title="{title}"></a>
        <div class="option-other d-block d-sm-none"><p class="date" title="28/10/2019 às 17:35">7 horas</p></div>
      </div>
      <div class="description">
        <h3><a href="{href}">{title}</a></h3>
        <p class="price"> {price} </p>
        <div class="option-store"><a href="{href}"><span>Ir para</span> {store}</a></div>
        <div class="option-other d-none d-sm-block"><p class="date" title="{posted}">7 horas</p></div>
      </div>
    </article>
    """
    return BeautifulSoup(html, "html.parser").select_one("article")


def test_card_to_raw_maps_fields_and_drops_the_aggregator_tag():
    raw = gd.card_to_raw(make_card())

    assert raw["id"].startswith("gatry_") and len(raw["id"]) == len("gatry_") + 12
    assert raw["title"] == "WAP Parafusadeira Impacto 3/8 700W"
    assert raw["price"] == 96.52
    assert raw["url"] == "https://www.amazon.com.br/WAP/dp/B0F678PCRM"  # sem a tag do Gatry
    assert raw["source"] == "Amazon"
    assert raw["image_url"] == "https://cdn.gatry.com/img/a.jpg"


def test_card_has_no_invented_list_price_or_free_shipping():
    raw = gd.card_to_raw(make_card())

    assert raw.get("list_price") is None
    assert raw["free_shipping"] == 0


@pytest.mark.parametrize(
    "label,expected",
    [
        ("Amazon", "Amazon"),
        ("Mercado Livre", "Mercado Livre"),
        ("Magalu", "Magazine Luiza"),
        ("Magazine Luiza", "Magazine Luiza"),
        ("KaBuM!", "KaBuM!"),
        ("Casas Bahia", "Casas Bahia"),
    ],
)
def test_store_name_normalizes_known_stores(label, expected):
    assert gd.store_name(label) == expected


@pytest.mark.parametrize(
    "overrides",
    [{"price": "Grátis"}, {"price": ""}, {"href": ""}, {"title": ""}],
)
def test_card_to_raw_rejects_incomplete_cards(overrides):
    assert gd.card_to_raw(make_card(**overrides)) is None


@pytest.mark.parametrize(
    "store,href",
    [
        ("Mercado Livre", "https://meli.la/1fogrET"),
        ("Amazon", "https://link.amazon/abc123"),
        ("Amazon", "https://amzn.to/3xYz"),
        ("Amazon", "https://www.amazon.com/dp/B000"),  # domínio errado para a Amazon Brasil
        ("Mercado Livre", "https://www.exemplo.com/produto/1"),
    ],
)
def test_links_we_cannot_tag_are_dropped(store, href):
    assert gd.card_to_raw(make_card(store=store, href=href)) is None


def test_direct_marketplace_links_are_kept():
    ml = gd.card_to_raw(make_card(store="Mercado Livre", href="https://produto.mercadolivre.com.br/MLB-123-fone?x=1"))

    assert ml["url"] == "https://produto.mercadolivre.com.br/MLB-123-fone"
    assert ml["source"] == "Mercado Livre"


def test_posted_at_converts_brazil_time_to_utc_and_ignores_bogus_dates():
    posted = gd.parse_posted_at(make_card(posted="26/10/2026 às 13:05"))

    assert posted == datetime(2026, 10, 26, 16, 5)


def test_is_fresh_uses_the_age_limit():
    assert gd.is_fresh(NOW - timedelta(hours=5), NOW, 72) is True
    assert gd.is_fresh(NOW - timedelta(hours=100), NOW, 72) is False
    assert gd.is_fresh(None, NOW, 72) is False


def test_collect_fresh_deals_stops_at_the_first_stale_page_and_dedupes():
    fresh = make_card(title="Oferta nova", posted="26/10/2026 às 15:00")
    duplicate = make_card(title="Oferta nova", posted="26/10/2026 às 15:00")
    stale = make_card(title="Oferta velha", posted="20/10/2026 às 10:00")
    pages = {1: [fresh, duplicate], 2: [stale], 3: [fresh]}
    calls = []

    def fetch(page):
        calls.append(page)
        return pages.get(page, [])

    deals = gd.collect_fresh_deals(fetch, NOW, max_pages=5, max_age_hours=72)

    assert [d["title"] for d in deals] == ["Oferta nova"]
    assert calls == [1, 2]
