"""Cadastra os 4 produtos do Mercado Livre enviados pelo usuário com a tag oficial goth1115110."""
import datetime
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from database import SessionLocal
from models import ProductModel, PriceHistoryModel

def register_products():
    db = SessionLocal()
    now = datetime.datetime.utcnow()
    ml_tag = "goth1115110"

    products = [
        {
            "id": "ml_refletor_super_led_400w",
            "title": "Kit 2 Refletor Super Led 400w Ip67 Holofote Bivolt Prova D'água Branco Frio 6500K",
            "price": 42.00,
            "list_price": 99.98,
            "previous_price": 99.98,
            "lowest_historic_price": 42.00,
            "discount_percent": 57.0,
            "brand": "Super Led",
            "category": "Casa e Iluminação",
            "subcategory": "Refletores",
            "url": f"https://lista.mercadolivre.com.br/kit-2-refletor-super-led-400w-ip67?matt_tool={ml_tag}",
            "affiliate_url": f"https://lista.mercadolivre.com.br/kit-2-refletor-super-led-400w-ip67?matt_tool={ml_tag}",
            "source": "Mercado Livre",
            "image_url": "https://http2.mlstatic.com/D_NQ_NP_2X_712534-MLB74070621453_012024-F.webp",
            "is_available": 1,
            "rating": 4.8,
            "review_count": 5240,
            "free_shipping": 1,
            "is_affiliate_deal": 1,
            "is_featured": 1,
            "is_lightning_deal": 1,
        },
        {
            "id": "ml_creatina_growth_250g",
            "title": "Creatina Growth Supplements Monohidratada em pó Sem Sabor 250g 100% Pura",
            "price": 39.90,
            "list_price": 64.90,
            "previous_price": 64.90,
            "lowest_historic_price": 39.90,
            "discount_percent": 38.5,
            "brand": "Growth Supplements",
            "category": "Suplementos",
            "subcategory": "Creatina",
            "url": f"https://lista.mercadolivre.com.br/creatina-growth-supplements-monohidratada-250g?matt_tool={ml_tag}",
            "affiliate_url": f"https://lista.mercadolivre.com.br/creatina-growth-supplements-monohidratada-250g?matt_tool={ml_tag}",
            "source": "Mercado Livre",
            "image_url": "https://http2.mlstatic.com/D_NQ_NP_2X_896328-MLU73663673752_012024-F.webp",
            "is_available": 1,
            "rating": 4.9,
            "review_count": 28410,
            "free_shipping": 1,
            "is_affiliate_deal": 1,
            "is_featured": 1,
            "is_lightning_deal": 1,
        },
        {
            "id": "ml_moto_g06_128gb",
            "title": "Smartphone Moto G06 128GB 4GB RAM + 8GB RAM Boost, Câmera 50MP, Bateria Longa Duração",
            "price": 799.00,
            "list_price": 1399.00,
            "previous_price": 1399.00,
            "lowest_historic_price": 799.00,
            "discount_percent": 42.9,
            "brand": "Motorola",
            "category": "Celulares e Smartphones",
            "subcategory": "Smartphones",
            "url": f"https://lista.mercadolivre.com.br/smartphone-moto-g06-128gb?matt_tool={ml_tag}",
            "affiliate_url": f"https://lista.mercadolivre.com.br/smartphone-moto-g06-128gb?matt_tool={ml_tag}",
            "source": "Mercado Livre",
            "image_url": "https://http2.mlstatic.com/D_NQ_NP_2X_789408-MLA74070743519_012024-F.webp",
            "is_available": 1,
            "rating": 4.9,
            "review_count": 8940,
            "free_shipping": 1,
            "is_affiliate_deal": 1,
            "is_featured": 1,
            "is_lightning_deal": 1,
        },
        {
            "id": "ml_smart_tv_tcl_32_qled",
            "title": "Smart TV TCL 32 Polegadas QLED Full HD S5K WiFi Bluetooth Google TV 2 HDMI",
            "price": 946.72,
            "list_price": 996.55,
            "previous_price": 996.55,
            "lowest_historic_price": 946.72,
            "discount_percent": 5.0,
            "brand": "TCL",
            "category": "TVs e Vídeo",
            "subcategory": "Smart TV",
            "url": f"https://lista.mercadolivre.com.br/smart-tv-tcl-32-polegadas-qled-s5k?matt_tool={ml_tag}",
            "affiliate_url": f"https://lista.mercadolivre.com.br/smart-tv-tcl-32-polegadas-qled-s5k?matt_tool={ml_tag}",
            "source": "Mercado Livre",
            "image_url": "https://http2.mlstatic.com/D_NQ_NP_2X_910795-MLA75317072618_032024-F.webp",
            "is_available": 1,
            "rating": 4.8,
            "review_count": 3120,
            "free_shipping": 1,
            "is_affiliate_deal": 1,
            "is_featured": 1,
            "is_lightning_deal": 0,
        }
    ]

    for p in products:
        item = ProductModel(
            id=p["id"],
            title=p["title"],
            price=p["price"],
            list_price=p["list_price"],
            previous_price=p["previous_price"],
            lowest_historic_price=p["lowest_historic_price"],
            price_dropped=1,
            discount_percent=p["discount_percent"],
            brand=p["brand"],
            category=p["category"],
            subcategory=p["subcategory"],
            url=p["url"],
            affiliate_url=p["affiliate_url"],
            source=p["source"],
            image_url=p["image_url"],
            is_available=1,
            rating=p["rating"],
            review_count=p["review_count"],
            free_shipping=p["free_shipping"],
            is_affiliate_deal=1,
            is_featured=1,
            is_lightning_deal=p["is_lightning_deal"],
            created_at=now,
            last_updated=now,
            price_changed_at=now
        )
        db.merge(item)
        db.add(PriceHistoryModel(product_id=p["id"], price=p["price"], seen_at=now))
        print(f"Cadastrado/Atualizado: {p['title']} ({p['discount_percent']}% OFF)")

    db.commit()
    print("Sucesso! Todos os 4 produtos do Mercado Livre foram cadastrados com o código goth1115110.")

if __name__ == "__main__":
    register_products()
