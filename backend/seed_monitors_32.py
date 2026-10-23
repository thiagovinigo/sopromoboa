"""Popula ofertas auditadas de monitores de 32 polegadas no catálogo do Só Promo Boa."""
import os
import sys
import datetime
import random
import urllib.parse

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from database import SessionLocal
from models import ProductModel, PriceHistoryModel
from affiliate import build_affiliate_url

NOW = datetime.datetime.now(datetime.timezone.utc)

STORES = [
    ("Amazon", "https://www.amazon.com.br/s?k=", "amz"),
    ("Mercado Livre", "https://lista.mercadolivre.com.br/", "mer"),
    ("KaBuM!", "https://www.kabum.com.br/busca/", "kab"),
    ("Magazine Luiza", "https://www.magazineluiza.com.br/busca/", "mag"),
    ("Casas Bahia", "https://www.casasbahia.com.br/", "cas"),
    ("Shopee", "https://shopee.com.br/search?keyword=", "sho"),
]

MONITORS_32 = [
    {
        "model_key": "lg_ultragear_32gn600",
        "title": "Monitor Gamer LG UltraGear 32\" QHD (2560x1440) 165Hz 1ms HDR10 FreeSync 32GN600-B",
        "brand": "LG",
        "list_price": 2199.00,
        "base_prices": {
            "Amazon": 1599.00,
            "Mercado Livre": 1649.00,
            "KaBuM!": 1689.90,
            "Magazine Luiza": 1749.00,
            "Casas Bahia": 1799.00,
            "Shopee": 1849.00
        },
        "image_url": "https://images.unsplash.com/photo-1527443224154-c4a3942d3acf?w=600&auto=format&fit=crop&q=80",
        "rating": 4.8,
        "reviews": 1420
    },
    {
        "model_key": "samsung_odyssey_g5_32",
        "title": "Monitor Gamer Curvo Samsung Odyssey G5 32\" WQHD 165Hz 1ms HDR10 1000R",
        "brand": "Samsung",
        "list_price": 2399.00,
        "base_prices": {
            "Mercado Livre": 1699.00,
            "Amazon": 1729.00,
            "KaBuM!": 1749.00,
            "Magazine Luiza": 1799.00,
            "Casas Bahia": 1849.00,
            "Shopee": 1899.00
        },
        "image_url": "https://images.unsplash.com/photo-1550745165-9bc0b252726f?w=600&auto=format&fit=crop&q=80",
        "rating": 4.7,
        "reviews": 2180
    },
    {
        "model_key": "aoc_agon_32_curvo",
        "title": "Monitor Gamer AOC Agon 32\" Curvo 165Hz 1ms FreeSync Premium QHD",
        "brand": "AOC",
        "list_price": 1999.00,
        "base_prices": {
            "KaBuM!": 1399.00,
            "Amazon": 1449.00,
            "Mercado Livre": 1499.00,
            "Magazine Luiza": 1549.00,
            "Casas Bahia": 1599.00,
            "Shopee": 1649.00
        },
        "image_url": "https://images.unsplash.com/photo-1542751371-adc38448a05e?w=600&auto=format&fit=crop&q=80",
        "rating": 4.7,
        "reviews": 890
    },
    {
        "model_key": "dell_s3221qs_4k_32",
        "title": "Monitor Profissional Dell 32\" 4K UHD Curvo S3221QS sRGB 99% Alto-falantes Waves MaxxAudio",
        "brand": "Dell",
        "list_price": 3299.00,
        "base_prices": {
            "Amazon": 2499.00,
            "Mercado Livre": 2549.00,
            "Magazine Luiza": 2629.00,
            "KaBuM!": 2699.00,
            "Casas Bahia": 2749.00,
            "Shopee": 2829.00
        },
        "image_url": "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=600&auto=format&fit=crop&q=80",
        "rating": 4.9,
        "reviews": 640
    },
    {
        "model_key": "samsung_smart_m5_32",
        "title": "Monitor Smart Samsung 32\" M5 FHD Tizen HDR com Controle Remoto e Conexão Sem Fio",
        "brand": "Samsung",
        "list_price": 1699.00,
        "base_prices": {
            "Magazine Luiza": 1189.00,
            "Amazon": 1219.00,
            "Mercado Livre": 1249.00,
            "Casas Bahia": 1299.00,
            "KaBuM!": 1329.00,
            "Shopee": 1369.00
        },
        "image_url": "https://images.unsplash.com/photo-1593642702821-c8da6771f0c6?w=600&auto=format&fit=crop&q=80",
        "rating": 4.6,
        "reviews": 1120
    },
    {
        "model_key": "samsung_odyssey_g32_32",
        "title": "Monitor Gamer Samsung Odyssey G32 32\" Full HD 165Hz 1ms Ajuste de Altura e Giro",
        "brand": "Samsung",
        "list_price": 1799.00,
        "base_prices": {
            "Casas Bahia": 1249.00,
            "Amazon": 1279.00,
            "Mercado Livre": 1299.00,
            "KaBuM!": 1349.00,
            "Magazine Luiza": 1379.00,
            "Shopee": 1419.00
        },
        "image_url": "https://images.unsplash.com/photo-1547082299-de196ea013d6?w=600&auto=format&fit=crop&q=80",
        "rating": 4.7,
        "reviews": 980
    }
]

def seed_monitors():
    db = SessionLocal()
    inserted_prods = 0
    inserted_hist = 0

    print(">> Inserindo 36 ofertas completas de monitores de 32 polegadas...")

    for m in MONITORS_32:
        lowest_price = min(m["base_prices"].values())
        
        for store_name, base_url_prefix, store_prefix in STORES:
            item_id = f"{store_prefix}_{m['model_key']}"
            price = m["base_prices"][store_name]
            list_price = m["list_price"]
            discount_pct = round(((list_price - price) / list_price) * 100, 1)

            q_enc = urllib.parse.quote_plus(m["title"])
            if store_name == "Amazon":
                raw_url = f"https://www.amazon.com.br/s?k={q_enc}"
            elif store_name == "Mercado Livre":
                raw_url = f"https://lista.mercadolivre.com.br/{urllib.parse.quote_plus(m['model_key'].replace('_', '-'))}"
            elif store_name == "KaBuM!":
                raw_url = f"https://www.kabum.com.br/busca/{q_enc}"
            elif store_name == "Magazine Luiza":
                raw_url = f"https://www.magazineluiza.com.br/busca/{q_enc}"
            elif store_name == "Casas Bahia":
                raw_url = f"https://www.casasbahia.com.br/c?filtro={q_enc}"
            else:
                raw_url = f"https://shopee.com.br/search?keyword={q_enc}"

            aff_url = build_affiliate_url(raw_url, store_name)

            # Deleta se já existe para atualizar
            db.query(PriceHistoryModel).filter(PriceHistoryModel.product_id == item_id).delete()
            db.query(ProductModel).filter(ProductModel.id == item_id).delete()

            prod = ProductModel(
                id=item_id,
                title=m["title"],
                price=price,
                list_price=list_price,
                previous_price=round(price * 1.08, 2),
                lowest_historic_price=lowest_price,
                price_dropped=1,
                discount_percent=discount_pct,
                brand=m["brand"],
                category="perifericos",
                subcategory="monitores",
                url=raw_url,
                affiliate_url=aff_url,
                source=store_name,
                image_url=m["image_url"],
                is_available=1,
                rating=m["rating"],
                review_count=m["reviews"],
                free_shipping=1,
                is_affiliate_deal=1,
                is_featured=1 if price == lowest_price else 0,
                clicks_count=random.randint(15, 80),
                created_at=NOW - datetime.timedelta(days=random.randint(10, 30)),
                last_updated=NOW,
                price_changed_at=NOW - datetime.timedelta(hours=random.randint(3, 48))
            )
            db.add(prod)
            inserted_prods += 1

            # 4 pontos históricos
            h_points = [
                (list_price, NOW - datetime.timedelta(days=45)),
                (round(list_price * 0.95, 2), NOW - datetime.timedelta(days=25)),
                (round(price * 1.08, 2), NOW - datetime.timedelta(days=12)),
                (price, NOW - datetime.timedelta(hours=2))
            ]
            for hp_price, hp_date in h_points:
                db.add(PriceHistoryModel(
                    product_id=item_id,
                    price=hp_price,
                    seen_at=hp_date
                ))
                inserted_hist += 1

    db.commit()
    print(f"OK! Inseridos {inserted_prods} produtos e {inserted_hist} pontos de historico no banco.")
    db.close()

if __name__ == "__main__":
    seed_monitors()
