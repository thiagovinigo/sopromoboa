"""Scraper e Minerador de Ofertas do Mercado Livre Brasil com Injeção de Afiliado.

Combina:
1. Varredura em tempo real de ofertas do Mercado Livre postadas em agregadores abertos (Gatry).
2. Curadoria ativa dos produtos campeões de vendas e maiores comissões (Ganhos Extras até 62%).
3. Injeção obrigatória da tag oficial do parceiro: goth1115110.
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

ML_AFFILIATE_TAG = "goth1115110"

# Catálogo flagships do Mercado Livre nos nichos mais lucrativos
ML_FLAGSHIPS = [
    {
        "id": "ml_refletor_super_led_400w",
        "title": "Kit 2 Refletor Super Led 400w Ip67 Holofote Bivolt Prova D'água Branco Frio 6500K",
        "price": 42.00,
        "list_price": 99.98,
        "brand": "Super Led",
        "category": "Casa e Iluminação",
        "url": f"https://lista.mercadolivre.com.br/kit-2-refletor-super-led-400w-ip67?matt_tool={ML_AFFILIATE_TAG}",
        "image_url": "https://http2.mlstatic.com/D_NQ_NP_2X_712534-MLB74070621453_012024-F.webp",
        "rating": 4.8,
        "free_shipping": 1,
    },
    {
        "id": "ml_creatina_growth_250g",
        "title": "Creatina Growth Supplements Monohidratada em pó Sem Sabor 250g 100% Pura",
        "price": 39.90,
        "list_price": 64.90,
        "brand": "Growth Supplements",
        "category": "Suplementos",
        "url": f"https://lista.mercadolivre.com.br/creatina-growth-supplements-monohidratada-250g?matt_tool={ML_AFFILIATE_TAG}",
        "image_url": "https://http2.mlstatic.com/D_NQ_NP_2X_896328-MLU73663673752_012024-F.webp",
        "rating": 4.9,
        "free_shipping": 1,
    },
    {
        "id": "ml_moto_g06_128gb",
        "title": "Smartphone Moto G06 128GB 4GB RAM + 8GB RAM Boost, Câmera 50MP, Bateria Longa Duração",
        "price": 799.00,
        "list_price": 1399.00,
        "brand": "Motorola",
        "category": "Celulares e Smartphones",
        "url": f"https://lista.mercadolivre.com.br/smartphone-moto-g06-128gb?matt_tool={ML_AFFILIATE_TAG}",
        "image_url": "https://http2.mlstatic.com/D_NQ_NP_2X_789408-MLA74070743519_012024-F.webp",
        "rating": 4.9,
        "free_shipping": 1,
    },
    {
        "id": "ml_smart_tv_tcl_32_qled",
        "title": "Smart TV TCL 32 Polegadas QLED Full HD S5K WiFi Bluetooth Google TV 2 HDMI",
        "price": 946.72,
        "list_price": 996.55,
        "brand": "TCL",
        "category": "TVs e Vídeo",
        "url": f"https://lista.mercadolivre.com.br/smart-tv-tcl-32-polegadas-qled-s5k?matt_tool={ML_AFFILIATE_TAG}",
        "image_url": "https://http2.mlstatic.com/D_NQ_NP_2X_910795-MLA75317072618_032024-F.webp",
        "rating": 4.8,
        "free_shipping": 1,
    },
    {
        "id": "ml_whey_growth_100_concentrado_1kg",
        "title": "100% Whey Concentrado Growth Supplements 1kg - Chocolate / Baunilha",
        "price": 108.00,
        "list_price": 149.90,
        "brand": "Growth Supplements",
        "category": "Suplementos",
        "url": f"https://lista.mercadolivre.com.br/whey-concentrado-growth-1kg?matt_tool={ML_AFFILIATE_TAG}",
        "image_url": "https://http2.mlstatic.com/D_NQ_NP_2X_917336-MLA73767855355_012024-F.webp",
        "rating": 4.9,
        "free_shipping": 1,
    },
    {
        "id": "ml_air_fryer_philco_15l_oven",
        "title": "Fritadeira Air Fryer Oven Philco 15L Dupla Resistência 1800W Inox",
        "price": 367.63,
        "list_price": 599.90,
        "brand": "Philco",
        "category": "Eletrodomésticos",
        "url": f"https://lista.mercadolivre.com.br/air-fryer-oven-philco-15l?matt_tool={ML_AFFILIATE_TAG}",
        "image_url": "https://http2.mlstatic.com/D_NQ_NP_2X_841793-MLA74070621453_012024-F.webp",
        "rating": 4.8,
        "free_shipping": 1,
    },
    {
        "id": "ml_extensao_eletrica_5_tomadas_usb",
        "title": "Extensão Elétrica 5 Tomadas + 6 Portas USB 2500W Régua Bivolt Cabo 2m",
        "price": 36.00,
        "list_price": 79.90,
        "brand": "Bivolt Pro",
        "category": "Ferramentas",
        "url": f"https://lista.mercadolivre.com.br/extensao-eletrica-5-tomadas-6-usb?matt_tool={ML_AFFILIATE_TAG}",
        "image_url": "https://http2.mlstatic.com/D_NQ_NP_2X_789408-MLA74070743519_012024-F.webp",
        "rating": 4.7,
        "free_shipping": 1,
    },
    {
        "id": "ml_robo_aspirador_wap_w100",
        "title": "Robô Aspirador de Pó WAP Robot W100 Bivolt Automático 3 em 1 Varre Aspira e Passa Pano",
        "price": 389.90,
        "list_price": 549.90,
        "brand": "WAP",
        "category": "Casa e Limpeza",
        "url": f"https://lista.mercadolivre.com.br/robo-aspirador-wap-w100?matt_tool={ML_AFFILIATE_TAG}",
        "image_url": "https://http2.mlstatic.com/D_NQ_NP_2X_705252-MLA75317072618_032024-F.webp",
        "rating": 4.8,
        "free_shipping": 1,
    }
]


def clean_ml_url(url: str, title: str) -> str:
    """Higieniza o link do Mercado Livre e injeta a tag do parceiro goth1115110."""
    if not url:
        slug = re.sub(r"[^\w\s-]", "", title).strip().replace(" ", "-").lower()
        return f"https://lista.mercadolivre.com.br/{slug}?matt_tool={ML_AFFILIATE_TAG}"

    # Se já tem matt_tool antigo, substitui
    if "matt_tool=" in url:
        return re.sub(r"matt_tool=[^&]+", f"matt_tool={ML_AFFILIATE_TAG}", url)

    # Se for link encurtado ou social
    if "mercadolivre.com" in url:
        sep = "&" if "?" in url else "?"
        return f"{url}{sep}matt_tool={ML_AFFILIATE_TAG}"

    slug = re.sub(r"[^\w\s-]", "", title).strip().replace(" ", "-").lower()
    return f"https://lista.mercadolivre.com.br/{slug}?matt_tool={ML_AFFILIATE_TAG}"


def scrape_mercadolivre() -> List[Dict[str, Any]]:
    """Minera ofertas do Mercado Livre em tempo real através dos agregadores e base curada."""
    results = []
    seen_ids = set()

    # 1. Carrega produtos campeões fixos do Mercado Livre
    for f in ML_FLAGSHIPS:
        results.append({
            "id": f["id"],
            "title": f["title"],
            "price": f["price"],
            "list_price": f["list_price"],
            "url": f["url"],
            "source": "Mercado Livre",
            "image_url": f["image_url"],
            "free_shipping": f.get("free_shipping", 1),
        })
        seen_ids.add(f["id"])

    # 2. Busca novidades do Mercado Livre no agregador aberto (Gatry)
    queries = ["mercado livre", "meli"]
    for q in queries:
        try:
            url = f"https://gatry.com/?q={urllib.parse.quote_plus(q)}"
            resp = requests.get(url, headers=HEADERS, timeout=8)
            if resp.status_code != 200:
                continue

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
                affiliate_url = clean_ml_url(raw_url, title)

                item_id = f"ml_{hashlib.md5(title.encode('utf-8')).hexdigest()[:12]}"
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
                    "list_price": round(price * 1.35, 2), # estimativa de preço original
                    "url": affiliate_url,
                    "source": "Mercado Livre",
                    "image_url": image_url,
                    "free_shipping": 1,
                })
        except Exception as e:
            print(f"[Minerador ML] Erro ao buscar '{q}': {e}")

    return results
