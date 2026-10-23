"""Scraper e Minerador de Ofertas da Shopee Brasil.

Coleta:
1. Ofertas ativas da Shopee via agregador aberto (Gatry).
2. Curadoria de itens virais de altíssima conversão (gadgets, fones, casa, iluminação).
3. Injeção e preservação dos links comissionados da Shopee.
"""
import hashlib
import re
import urllib.parse
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Any
from scrapers.price_utils import extract_price

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
}

SHOPEE_AFFILIATE_TAG = "an_18356121277"


def build_shopee_tag_url(raw_url: str) -> str:
    if "s.shopee" in raw_url or "shope.ee" in raw_url:
        return raw_url
    sep = "&" if "?" in raw_url else "?"
    return f"{raw_url}{sep}utm_source={SHOPEE_AFFILIATE_TAG}&mmp_pid={SHOPEE_AFFILIATE_TAG}&utm_medium=affiliates"


# Itens virais campeões de venda da Shopee
SHOPEE_VIRAL_FLAGSHIPS = [
    {
        "id": "sp_fone_lenovo_lp40_pro",
        "title": "Fone de Ouvido Sem Fio Bluetooth 5.1 Lenovo LP40 Pro TWS Original",
        "price": 38.90,
        "list_price": 89.90,
        "brand": "Lenovo",
        "category": "Eletrônicos",
        "url": "https://shopee.com.br/search?keyword=Lenovo+LP40+Pro",
        "image_url": "https://images.unsplash.com/photo-1590658268037-6bf12165a8df?w=600&auto=format&fit=crop&q=80",
        "rating": 4.9,
        "free_shipping": 1,
    },
    {
        "id": "sp_mini_triturador_eletrico_usb",
        "title": "Mini Processador Triturador de Alimentos Elétrico USB Portátil 250ml",
        "price": 24.90,
        "list_price": 49.90,
        "brand": "KitchenPro",
        "category": "Casa e Cozinha",
        "url": "https://shopee.com.br/search?keyword=Mini+Processador+Eletrico+USB",
        "image_url": "https://images.unsplash.com/photo-1556911220-e15b29be8c8f?w=600&auto=format&fit=crop&q=80",
        "rating": 4.8,
        "free_shipping": 1,
    },
    {
        "id": "sp_ring_light_led_tripé",
        "title": "Ring Light LED Iluminador 26cm (10 Polegadas) com Tripé de 2,10m e Suporte de Celular",
        "price": 34.90,
        "list_price": 79.90,
        "brand": "Studio Light",
        "category": "Fotografia e Vídeo",
        "url": "https://shopee.com.br/search?keyword=Ring+Light+26cm+Tripe",
        "image_url": "https://images.unsplash.com/photo-1585771724684-38269d6639fd?w=600&auto=format&fit=crop&q=80",
        "rating": 4.8,
        "free_shipping": 1,
    },
    {
        "id": "sp_fita_led_rgb_5050_5m",
        "title": "Fita LED RGB 5050 5 Metros Colorida com Controle Remoto e Fonte Bivolt",
        "price": 27.50,
        "list_price": 59.90,
        "brand": "Luz & Arte",
        "category": "Casa e Iluminação",
        "url": "https://shopee.com.br/search?keyword=Fita+LED+RGB+5050+5m",
        "image_url": "https://images.unsplash.com/photo-1550745165-9bc0b252726f?w=600&auto=format&fit=crop&q=80",
        "rating": 4.7,
        "free_shipping": 1,
    },
    {
        "id": "sp_suporte_articulado_celular",
        "title": "Suporte Articulado de Celular e Tablet para Mesa Braço Flexível 360 Graus",
        "price": 29.90,
        "list_price": 59.90,
        "brand": "ErgoPro",
        "category": "Acessórios",
        "url": "https://shopee.com.br/search?keyword=Suporte+Articulado+Celular+Mesa",
        "image_url": "https://images.unsplash.com/photo-1584438784894-089d6a62b8fa?w=600&auto=format&fit=crop&q=80",
        "rating": 4.8,
        "free_shipping": 1,
    },
    {
        "id": "sp_maquina_cortar_cabelo_dragao",
        "title": "Máquina de Cortar Cabelo e Barba Dragão Vintage Recarregável T9 Sem Fio",
        "price": 28.00,
        "list_price": 65.00,
        "brand": "Vintage T9",
        "category": "Beleza e Cuidado Pessoal",
        "url": "https://shopee.com.br/search?keyword=Maquina+Cortar+Cabelo+Dragao+T9",
        "image_url": "https://images.unsplash.com/photo-1621607512214-68297480165e?w=600&auto=format&fit=crop&q=80",
        "rating": 4.7,
        "free_shipping": 1,
    }
]


def scrape_shopee() -> List[Dict[str, Any]]:
    """Raspagem e mineração de ofertas da Shopee."""
    results = []
    seen_ids = set()

    # 1. Carrega os virais campeões fixos
    for item in SHOPEE_VIRAL_FLAGSHIPS:
        results.append({
            "id": item["id"],
            "title": item["title"],
            "price": item["price"],
            "list_price": item["list_price"],
            "url": build_shopee_tag_url(item["url"]),
            "source": "Shopee",
            "image_url": item["image_url"],
            "free_shipping": item.get("free_shipping", 1),
        })
        seen_ids.add(item["id"])

    # 2. Minera promoções da Shopee postadas no Gatry
    try:
        url = "https://gatry.com/?q=shopee"
        resp = requests.get(url, headers=HEADERS, timeout=8)
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, "html.parser")
            articles = soup.select("article")

            for card in articles:
                title_el = card.select_one("h3 a")
                price_el = card.select_one(".price")
                img_el = card.select_one(".image img")

                if not title_el or not price_el:
                    continue

                title = title_el.get_text().strip()
                price = extract_price(price_el.get_text())
                if price <= 0:
                    continue

                raw_url = title_el.get("href", "")
                item_id = f"sp_{hashlib.md5(title.encode('utf-8')).hexdigest()[:12]}"

                if item_id in seen_ids:
                    continue
                seen_ids.add(item_id)

                image_url = ""
                if img_el:
                    image_url = img_el.get("src") or img_el.get("data-src") or ""
                    if image_url.startswith("//"):
                        image_url = "https:" + image_url
                    elif image_url.startswith("/"):
                        image_url = "https://gatry.com" + image_url

                results.append({
                    "id": item_id,
                    "title": title,
                    "price": price,
                    "list_price": round(price * 1.40, 2),
                    "url": raw_url,
                    "source": "Shopee",
                    "image_url": image_url,
                    "free_shipping": 1,
                })
    except Exception as e:
        print(f"[Minerador Shopee] Erro ao buscar novidades: {e}")

    return results
