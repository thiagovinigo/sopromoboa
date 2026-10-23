import sqlite3

conn = sqlite3.connect("c:/Users/User/sopromoboa/backend/sopromoboa.db")
cur = conn.cursor()

# Check if is_lightning_deal column exists in products
cur.execute("PRAGMA table_info(products);")
cols = [c[1] for c in cur.fetchall()]
if "is_lightning_deal" not in cols:
    cur.execute("ALTER TABLE products ADD COLUMN is_lightning_deal INTEGER DEFAULT 0;")
    print("Added is_lightning_deal column to products table!")
else:
    print("is_lightning_deal already exists.")

# Mark top deals with discount >= 25% as lightning deals
cur.execute("UPDATE products SET is_lightning_deal = 1 WHERE discount_percent >= 25;")
print("Updated lightning deals based on discount >= 25%!")

# Seed Fire TV Stick and top Amazon flash deals
fire_tv_deals = [
    {
        "id": "amz_fire_tv_stick_hd",
        "title": "Fire TV Stick HD com Controle Remoto por Voz com Alexa",
        "price": 249.00,
        "list_price": 349.00,
        "previous_price": 349.00,
        "lowest_historic_price": 239.00,
        "price_dropped": 1,
        "discount_percent": 28.6,
        "brand": "Amazon",
        "category": "eletronicos",
        "subcategory": "streaming",
        "url": "https://www.amazon.com.br/dp/B0B5PZ4MQ9?tag=thiagovinigo-20",
        "affiliate_url": "https://www.amazon.com.br/dp/B0B5PZ4MQ9?tag=thiagovinigo-20",
        "source": "Amazon",
        "image_url": "https://m.media-amazon.com/images/I/51wXhS7vQLL._AC_SL1000_.jpg",
        "is_available": 1,
        "rating": 4.8,
        "review_count": 14200,
        "free_shipping": 1,
        "is_affiliate_deal": 1,
        "is_featured": 1,
        "is_lightning_deal": 1
    },
    {
        "id": "amz_fire_tv_stick_4k",
        "title": "Fire TV Stick 4K com Suporte a Dolby Vision, Dolby Atmos e Wi-Fi 6",
        "price": 379.00,
        "list_price": 449.00,
        "previous_price": 449.00,
        "lowest_historic_price": 359.00,
        "price_dropped": 1,
        "discount_percent": 15.6,
        "brand": "Amazon",
        "category": "eletronicos",
        "subcategory": "streaming",
        "url": "https://www.amazon.com.br/dp/B0BP9L3G22?tag=thiagovinigo-20",
        "affiliate_url": "https://www.amazon.com.br/dp/B0BP9L3G22?tag=thiagovinigo-20",
        "source": "Amazon",
        "image_url": "https://m.media-amazon.com/images/I/51VbVwvi5uL._AC_SL1000_.jpg",
        "is_available": 1,
        "rating": 4.9,
        "review_count": 8900,
        "free_shipping": 1,
        "is_affiliate_deal": 1,
        "is_featured": 1,
        "is_lightning_deal": 1
    },
    {
        "id": "amz_echo_dot_5",
        "title": "Echo Dot 5ª geração | Smart Speaker com Alexa e Áudio Imersivo",
        "price": 349.00,
        "list_price": 429.00,
        "previous_price": 429.00,
        "lowest_historic_price": 319.00,
        "price_dropped": 1,
        "discount_percent": 18.6,
        "brand": "Amazon",
        "category": "casa",
        "subcategory": "alexa",
        "url": "https://www.amazon.com.br/dp/B09B8V1LZ3?tag=thiagovinigo-20",
        "affiliate_url": "https://www.amazon.com.br/dp/B09B8V1LZ3?tag=thiagovinigo-20",
        "source": "Amazon",
        "image_url": "https://m.media-amazon.com/images/I/71C8z+V-QjL._AC_SL1000_.jpg",
        "is_available": 1,
        "rating": 4.8,
        "review_count": 25400,
        "free_shipping": 1,
        "is_affiliate_deal": 1,
        "is_featured": 1,
        "is_lightning_deal": 1
    },
    {
        "id": "amz_creatina_creapure_dux",
        "title": "Creatina Creapure DUX Nutrition 100% Pura 300g",
        "price": 149.90,
        "list_price": 199.90,
        "previous_price": 199.90,
        "lowest_historic_price": 139.90,
        "price_dropped": 1,
        "discount_percent": 25.0,
        "brand": "DUX",
        "category": "saude",
        "subcategory": "suplementos",
        "url": "https://www.amazon.com.br/dp/B0855G6L43?tag=thiagovinigo-20",
        "affiliate_url": "https://www.amazon.com.br/dp/B0855G6L43?tag=thiagovinigo-20",
        "source": "Amazon",
        "image_url": "https://m.media-amazon.com/images/I/61p-LqG7YnL._AC_SL1000_.jpg",
        "is_available": 1,
        "rating": 4.9,
        "review_count": 18300,
        "free_shipping": 1,
        "is_affiliate_deal": 1,
        "is_featured": 1,
        "is_lightning_deal": 1
    },
    {
        "id": "amz_airfryer_philips_walita",
        "title": "Fritadeira Sem Óleo Airfryer Philips Walita Série 1000 4.1L 1400W",
        "price": 399.00,
        "list_price": 549.90,
        "previous_price": 549.90,
        "lowest_historic_price": 389.00,
        "price_dropped": 1,
        "discount_percent": 27.4,
        "brand": "Philips Walita",
        "category": "eletrodomesticos",
        "subcategory": "cozinha",
        "url": "https://www.amazon.com.br/dp/B0BZF57N7H?tag=thiagovinigo-20",
        "affiliate_url": "https://www.amazon.com.br/dp/B0BZF57N7H?tag=thiagovinigo-20",
        "source": "Amazon",
        "image_url": "https://m.media-amazon.com/images/I/51uU+G-9mYL._AC_SL1000_.jpg",
        "is_available": 1,
        "rating": 4.8,
        "review_count": 9200,
        "free_shipping": 1,
        "is_affiliate_deal": 1,
        "is_featured": 1,
        "is_lightning_deal": 1
    }
]

for d in fire_tv_deals:
    cur.execute("""
        INSERT OR REPLACE INTO products (
            id, title, price, list_price, previous_price, lowest_historic_price,
            price_dropped, discount_percent, brand, category, subcategory,
            url, affiliate_url, source, image_url, is_available, rating,
            review_count, free_shipping, is_affiliate_deal, is_featured, is_lightning_deal
        ) VALUES (
            :id, :title, :price, :list_price, :previous_price, :lowest_historic_price,
            :price_dropped, :discount_percent, :brand, :category, :subcategory,
            :url, :affiliate_url, :source, :image_url, :is_available, :rating,
            :review_count, :free_shipping, :is_affiliate_deal, :is_featured, :is_lightning_deal
        )
    """, d)

conn.commit()

cur.execute("SELECT count(*) FROM products WHERE is_lightning_deal = 1")
print(f"Total de Ofertas Relâmpago ativas: {cur.fetchone()[0]}")

conn.close()
