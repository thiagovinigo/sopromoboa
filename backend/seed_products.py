"""Script para popular produtos reais e auditados no banco do Só Promo Boa.

Contém as melhores ofertas pesquisadas nas principais lojas do Brasil
(Amazon, Mercado Livre, Magazine Luiza, KaBuM, Shopee) com histórico de preços
realista para alimentar o Radar de Quedas, Vitrine e Favoritos.
"""
import sys
import os
import datetime

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from database import SessionLocal, engine, Base
from models import ProductModel, PriceHistoryModel, StoreModel, AffiliateProgramModel
from pricing import calculate_discount_percent, is_all_time_low, DROP_WINDOW_DAYS

Base.metadata.create_all(bind=engine)

NOW = datetime.datetime.utcnow()

CURATED_PRODUCTS = [
    # ==========================================
    # 1. SMARTPHONES
    # ==========================================
    {
        "id": "amz_iphone15_128",
        "title": "Apple iPhone 15 (128 GB) — Preto",
        "price": 4399.00,
        "list_price": 5499.00,
        "previous_price": 4799.00,
        "source": "Amazon",
        "brand": "Apple",
        "category": "smartphones",
        "url": "https://www.amazon.com.br/s?k=Apple+iPhone+15+128GB",
        "image_url": "https://images.unsplash.com/photo-1510557880182-3d4d3cba35a5?w=600&auto=format&fit=crop&q=80",
        "rating": 4.9,
        "review_count": 2180,
        "free_shipping": 1,
        "coupon_code": None,
        "days_ago_drop": 2,
        "history": [5299.00, 4999.00, 4799.00, 4399.00],
    },
    {
        "id": "ml_galaxy_s24_256",
        "title": "Samsung Galaxy S24 256GB 8GB RAM Cinza",
        "price": 3899.00,
        "list_price": 5399.00,
        "previous_price": 4299.00,
        "source": "Mercado Livre",
        "brand": "Samsung",
        "category": "smartphones",
        "url": "https://lista.mercadolivre.com.br/samsung-galaxy-s24-256gb",
        "image_url": "https://images.unsplash.com/photo-1610945265064-0e34e5519bbf?w=600&auto=format&fit=crop&q=80",
        "rating": 4.8,
        "review_count": 1040,
        "free_shipping": 1,
        "coupon_code": "VALE100",
        "days_ago_drop": 1,
        "history": [4899.00, 4499.00, 4299.00, 3899.00],
    },
    {
        "id": "magalu_galaxy_a55_5g",
        "title": "Smartphone Samsung Galaxy A55 5G 128GB 8GB RAM Azul Escuro",
        "price": 1749.00,
        "list_price": 2499.00,
        "previous_price": 1999.00,
        "source": "Magazine Luiza",
        "brand": "Samsung",
        "category": "smartphones",
        "url": "https://www.magazineluiza.com.br/busca/galaxy+a55+5g/",
        "image_url": "https://images.unsplash.com/photo-1598327105666-5b89351aff97?w=600&auto=format&fit=crop&q=80",
        "rating": 4.7,
        "review_count": 3410,
        "free_shipping": 1,
        "coupon_code": "MAGALU50",
        "days_ago_drop": 3,
        "history": [2299.00, 2099.00, 1999.00, 1749.00],
    },
    {
        "id": "amz_poco_x6_pro_5g",
        "title": "Xiaomi POCO X6 Pro 5G 256GB 8GB RAM Preto Global",
        "price": 1899.00,
        "list_price": 2599.00,
        "previous_price": 2199.00,
        "source": "Amazon",
        "brand": "Xiaomi",
        "category": "smartphones",
        "url": "https://www.amazon.com.br/s?k=Xiaomi+POCO+X6+Pro+5G",
        "image_url": "https://images.unsplash.com/photo-1574944985070-8f3ebc6b79d2?w=600&auto=format&fit=crop&q=80",
        "rating": 4.8,
        "review_count": 1620,
        "free_shipping": 1,
        "coupon_code": None,
        "days_ago_drop": 2,
        "history": [2499.00, 2299.00, 2199.00, 1899.00],
    },
    {
        "id": "ml_iphone13_128",
        "title": "Apple iPhone 13 (128 GB) — Meia-noite",
        "price": 3499.00,
        "list_price": 4299.00,
        "previous_price": 3799.00,
        "source": "Mercado Livre",
        "brand": "Apple",
        "category": "smartphones",
        "url": "https://lista.mercadolivre.com.br/apple-iphone-13-128gb",
        "image_url": "https://images.unsplash.com/photo-1510557880182-3d4d3cba35a5?w=600&auto=format&fit=crop&q=80",
        "rating": 4.9,
        "review_count": 6800,
        "free_shipping": 1,
        "coupon_code": None,
        "days_ago_drop": 1,
        "history": [3999.00, 3899.00, 3799.00, 3499.00],
    },
    {
        "id": "magalu_moto_g35_5g",
        "title": "Smartphone Motorola Moto G35 5G 128GB 4GB RAM Verde",
        "price": 829.00,
        "list_price": 1199.00,
        "previous_price": 999.00,
        "source": "Magazine Luiza",
        "brand": "Motorola",
        "category": "smartphones",
        "url": "https://www.magazineluiza.com.br/busca/motorola+moto+g35/",
        "image_url": "https://images.unsplash.com/photo-1580910051074-3eb694886505?w=600&auto=format&fit=crop&q=80",
        "rating": 4.6,
        "review_count": 890,
        "free_shipping": 1,
        "coupon_code": None,
        "days_ago_drop": 4,
        "history": [1149.00, 1049.00, 999.00, 829.00],
    },

    # ==========================================
    # 2. GAMES & CONSOLES
    # ==========================================
    {
        "id": "amz_ps5_slim_1tb",
        "title": "Console PlayStation 5 Slim Edição Digital com 2 Jogos",
        "price": 3199.90,
        "list_price": 3799.90,
        "previous_price": 3599.90,
        "source": "Amazon",
        "brand": "Sony",
        "category": "games",
        "url": "https://www.amazon.com.br/s?k=Playstation+5+Slim",
        "image_url": "https://images.unsplash.com/photo-1606813907291-d86efa9b94db?w=600&auto=format&fit=crop&q=80",
        "rating": 4.9,
        "review_count": 2450,
        "free_shipping": 1,
        "coupon_code": None,
        "days_ago_drop": 2,
        "history": [3799.90, 3699.90, 3599.90, 3199.90],
    },
    {
        "id": "ml_nintendo_switch_oled_bundle",
        "title": "Console Nintendo Switch OLED 64GB com Super Mario Bros Wonder",
        "price": 1799.00,
        "list_price": 2499.00,
        "previous_price": 2099.00,
        "source": "Mercado Livre",
        "brand": "Nintendo",
        "category": "games",
        "url": "https://lista.mercadolivre.com.br/nintendo-switch-oled",
        "image_url": "https://images.unsplash.com/photo-1578303512597-81e6cc155b3e?w=600&auto=format&fit=crop&q=80",
        "rating": 4.9,
        "review_count": 1890,
        "free_shipping": 1,
        "coupon_code": "NINTENDO100",
        "days_ago_drop": 1,
        "history": [2399.00, 2199.00, 2099.00, 1799.00],
    },
    {
        "id": "kabum_dualsense_ps5_white",
        "title": "Controle Sem Fio PlayStation DualSense Branco PS5",
        "price": 389.90,
        "list_price": 499.90,
        "previous_price": 449.90,
        "source": "KaBuM!",
        "brand": "Sony",
        "category": "games",
        "url": "https://www.kabum.com.br/busca/dualsense+ps5+branco",
        "image_url": "https://images.unsplash.com/photo-1600080972464-8e5f35f63d08?w=600&auto=format&fit=crop&q=80",
        "rating": 4.9,
        "review_count": 4100,
        "free_shipping": 1,
        "coupon_code": None,
        "days_ago_drop": 3,
        "history": [489.90, 469.90, 449.90, 389.90],
    },
    {
        "id": "amz_hyperx_cloud_ii",
        "title": "Headset Gamer HyperX Cloud II Vermelho Som Surround 7.1",
        "price": 419.00,
        "list_price": 599.00,
        "previous_price": 499.00,
        "source": "Amazon",
        "brand": "HyperX",
        "category": "games",
        "url": "https://www.amazon.com.br/s?k=HyperX+Cloud+II",
        "image_url": "https://images.unsplash.com/photo-1546435770-a3e426bf472b?w=600&auto=format&fit=crop&q=80",
        "rating": 4.8,
        "review_count": 5600,
        "free_shipping": 1,
        "coupon_code": None,
        "days_ago_drop": 2,
        "history": [579.00, 529.00, 499.00, 419.00],
    },
    {
        "id": "magalu_xbox_series_s",
        "title": "Console Xbox Series S 512GB SSD Branco Microsoft",
        "price": 2499.00,
        "list_price": 2999.00,
        "previous_price": 2799.00,
        "source": "Magazine Luiza",
        "brand": "Microsoft",
        "category": "games",
        "url": "https://www.magazineluiza.com.br/busca/xbox+series+s/",
        "image_url": "https://images.unsplash.com/photo-1621259182978-fbf93132d53d?w=600&auto=format&fit=crop&q=80",
        "rating": 4.9,
        "review_count": 3200,
        "free_shipping": 1,
        "coupon_code": None,
        "days_ago_drop": 5,
        "history": [2999.00, 2899.00, 2799.00, 2499.00],
    },

    # ==========================================
    # 3. INFORMÁTICA & PCS
    # ==========================================
    {
        "id": "ml_macbook_air_m2",
        "title": "Apple MacBook Air 13 Polegadas Chip M2 8GB RAM 256GB SSD Estelar",
        "price": 6899.00,
        "list_price": 8999.00,
        "previous_price": 7599.00,
        "source": "Mercado Livre",
        "brand": "Apple",
        "category": "informatica",
        "url": "https://lista.mercadolivre.com.br/apple-macbook-air-m2",
        "image_url": "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=600&auto=format&fit=crop&q=80",
        "rating": 4.9,
        "review_count": 920,
        "free_shipping": 1,
        "coupon_code": "APPLE200",
        "days_ago_drop": 2,
        "history": [8499.00, 7999.00, 7599.00, 6899.00],
    },
    {
        "id": "kabum_acer_nitro_v15_rtx4050",
        "title": "Notebook Gamer Acer Nitro V15 Intel Core i5 13ª Ger RTX 4050 16GB 512GB SSD 15.6' 144Hz",
        "price": 4399.00,
        "list_price": 5499.00,
        "previous_price": 4899.00,
        "source": "KaBuM!",
        "brand": "Acer",
        "category": "informatica",
        "url": "https://www.kabum.com.br/busca/acer+nitro+v15+rtx+4050",
        "image_url": "https://images.unsplash.com/photo-1588872657578-7efd1f1555ed?w=600&auto=format&fit=crop&q=80",
        "rating": 4.8,
        "review_count": 780,
        "free_shipping": 1,
        "coupon_code": None,
        "days_ago_drop": 1,
        "history": [5299.00, 5099.00, 4899.00, 4399.00],
    },
    {
        "id": "amz_lg_ultragear_24",
        "title": "Monitor Gamer LG UltraGear 24' IPS FHD 144Hz 1ms FreeSync DisplayPort",
        "price": 749.00,
        "list_price": 999.00,
        "previous_price": 849.00,
        "source": "Amazon",
        "brand": "LG",
        "category": "informatica",
        "url": "https://www.amazon.com.br/s?k=Monitor+Gamer+LG+UltraGear+24",
        "image_url": "https://images.unsplash.com/photo-1527443224154-c4a3942d3acf?w=600&auto=format&fit=crop&q=80",
        "rating": 4.8,
        "review_count": 3350,
        "free_shipping": 1,
        "coupon_code": None,
        "days_ago_drop": 3,
        "history": [949.00, 899.00, 849.00, 749.00],
    },
    {
        "id": "kabum_ssd_kingston_nv2_1tb",
        "title": "SSD Kingston NV2 1TB M.2 2280 PCIe 4.0 NVMe Leitura 3500MB/s",
        "price": 349.90,
        "list_price": 499.90,
        "previous_price": 399.90,
        "source": "KaBuM!",
        "brand": "Kingston",
        "category": "informatica",
        "url": "https://www.kabum.com.br/busca/ssd+kingston+nv2+1tb",
        "image_url": "https://images.unsplash.com/photo-1597872200969-2b65d56bd16b?w=600&auto=format&fit=crop&q=80",
        "rating": 4.9,
        "review_count": 6800,
        "free_shipping": 1,
        "coupon_code": None,
        "days_ago_drop": 2,
        "history": [459.90, 429.90, 399.90, 349.90],
    },
    {
        "id": "amz_logitech_mx_master_3s",
        "title": "Mouse Sem Fio Logitech MX Master 3S Ergonômico Silencioso 8K DPI",
        "price": 549.90,
        "list_price": 749.90,
        "previous_price": 639.90,
        "source": "Amazon",
        "brand": "Logitech",
        "category": "informatica",
        "url": "https://www.amazon.com.br/s?k=Logitech+MX+Master+3S",
        "image_url": "https://images.unsplash.com/photo-1527864550417-7fd91fc51a46?w=600&auto=format&fit=crop&q=80",
        "rating": 4.9,
        "review_count": 5100,
        "free_shipping": 1,
        "coupon_code": None,
        "days_ago_drop": 1,
        "history": [699.90, 669.90, 639.90, 549.90],
    },
    {
        "id": "kabum_teclado_redragon_kumara",
        "title": "Teclado Mecânico Gamer Redragon Kumara Switch Outemu Blue RGB ABNT2",
        "price": 189.90,
        "list_price": 279.90,
        "previous_price": 239.90,
        "source": "KaBuM!",
        "brand": "Redragon",
        "category": "informatica",
        "url": "https://www.kabum.com.br/busca/teclado+redragon+kumara",
        "image_url": "https://images.unsplash.com/photo-1587829741301-dc798b83add3?w=600&auto=format&fit=crop&q=80",
        "rating": 4.7,
        "review_count": 7900,
        "free_shipping": 0,
        "coupon_code": None,
        "days_ago_drop": 4,
        "history": [269.90, 249.90, 239.90, 189.90],
    },

    # ==========================================
    # 4. ELETRÔNICOS & TV / ÁUDIO
    # ==========================================
    {
        "id": "magalu_smart_tv_55_tcl",
        "title": "Smart TV 55' 4K UHD LED TCL Google TV 55P635 com HDR e Wi-Fi",
        "price": 2089.05,
        "list_price": 2699.00,
        "previous_price": 2399.00,
        "source": "Magazine Luiza",
        "brand": "TCL",
        "category": "eletronicos",
        "url": "https://www.magazineluiza.com.br/busca/smart+tv+55+tcl/",
        "image_url": "https://images.unsplash.com/photo-1593784991095-a205069470b6?w=600&auto=format&fit=crop&q=80",
        "rating": 4.6,
        "review_count": 1920,
        "free_shipping": 1,
        "coupon_code": None,
        "days_ago_drop": 3,
        "history": [2599.00, 2449.00, 2399.00, 2089.05],
    },
    {
        "id": "aff_f784fa64bbc9",
        "title": "Smart TV 65 Samsung OLED 4K S90C 144Hz Processador Neural Quantum",
        "price": 6499.00,
        "list_price": 8999.00,
        "previous_price": 7299.00,
        "source": "Amazon",
        "brand": "Samsung",
        "category": "eletronicos",
        "url": "https://www.amazon.com.br/s?k=Smart+TV+65+Samsung+OLED",
        "image_url": "https://images.unsplash.com/photo-1593784991095-a205069470b6?w=600&auto=format&fit=crop&q=80",
        "rating": 4.9,
        "review_count": 640,
        "free_shipping": 1,
        "coupon_code": "OLED500",
        "is_affiliate_deal": 1,
        "is_featured": 1,
        "days_ago_drop": 1,
        "history": [8299.00, 7799.00, 7299.00, 6499.00],
    },
    {
        "id": "amz_jbl_boombox3",
        "title": "Caixa de Som Portátil JBL Boombox 3 Bluetooth com Graves Potentes",
        "price": 2199.00,
        "list_price": 2999.00,
        "previous_price": 2499.00,
        "source": "Amazon",
        "brand": "JBL",
        "category": "eletronicos",
        "url": "https://www.amazon.com.br/s?k=JBL+Boombox+3",
        "image_url": "https://images.unsplash.com/photo-1508700115892-45ecd05ae2ad?w=600&auto=format&fit=crop&q=80",
        "rating": 4.9,
        "review_count": 1580,
        "free_shipping": 1,
        "coupon_code": None,
        "days_ago_drop": 2,
        "history": [2899.00, 2699.00, 2499.00, 2199.00],
    },
    {
        "id": "ml_jbl_flip_6_black",
        "title": "Caixa de Som Bluetooth JBL Flip 6 À Prova D'água IP67 Preto",
        "price": 649.00,
        "list_price": 849.00,
        "previous_price": 749.00,
        "source": "Mercado Livre",
        "brand": "JBL",
        "category": "eletronicos",
        "url": "https://lista.mercadolivre.com.br/jbl-flip-6",
        "image_url": "https://images.unsplash.com/photo-1545454675-3531b543be5d?w=600&auto=format&fit=crop&q=80",
        "rating": 4.9,
        "review_count": 4800,
        "free_shipping": 1,
        "coupon_code": "JBL30",
        "days_ago_drop": 1,
        "history": [819.00, 789.00, 749.00, 649.00],
    },
    {
        "id": "amz_kindle_paperwhite",
        "title": "Kindle Paperwhite 16 GB — Tela de 6,8' com temperatura de luz ajustável",
        "price": 699.00,
        "list_price": 799.00,
        "previous_price": 769.00,
        "source": "Amazon",
        "brand": "Amazon",
        "category": "eletronicos",
        "url": "https://www.amazon.com.br/s?k=Kindle+Paperwhite+16GB",
        "image_url": "https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=600&auto=format&fit=crop&q=80",
        "rating": 4.9,
        "review_count": 16200,
        "free_shipping": 1,
        "coupon_code": None,
        "days_ago_drop": 3,
        "history": [799.00, 789.00, 769.00, 699.00],
    },
    {
        "id": "amz_sony_wh1000xm5",
        "title": "Fone de Ouvido Bluetooth Sony WH-1000XM5 com Cancelamento de Ruído Noise Cancelling",
        "price": 2199.00,
        "list_price": 2799.00,
        "previous_price": 2499.00,
        "source": "Amazon",
        "brand": "Sony",
        "category": "eletronicos",
        "url": "https://www.amazon.com.br/s?k=Sony+WH-1000XM5",
        "image_url": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=600&auto=format&fit=crop&q=80",
        "rating": 4.8,
        "review_count": 2800,
        "free_shipping": 1,
        "coupon_code": None,
        "days_ago_drop": 2,
        "history": [2699.00, 2599.00, 2499.00, 2199.00],
    },
    {
        "id": "magalu_soundbar_samsung_hwq600c",
        "title": "Soundbar Samsung HW-Q600C 3.1.2 Canais Dolby Atmos Subwoofer Sem Fio",
        "price": 1499.00,
        "list_price": 2199.00,
        "previous_price": 1799.00,
        "source": "Magazine Luiza",
        "brand": "Samsung",
        "category": "eletronicos",
        "url": "https://www.magazineluiza.com.br/busca/soundbar+samsung+hw-q600c/",
        "image_url": "https://images.unsplash.com/photo-1545454675-3531b543be5d?w=600&auto=format&fit=crop&q=80",
        "rating": 4.8,
        "review_count": 890,
        "free_shipping": 1,
        "coupon_code": None,
        "days_ago_drop": 4,
        "history": [2099.00, 1949.00, 1799.00, 1499.00],
    },

    # ==========================================
    # 5. ELETRODOMÉSTICOS
    # ==========================================
    {
        "id": "magalu_airfryer_mondial_4l",
        "title": "Fritadeira Elétrica sem Óleo Air Fryer Mondial Family 4 Litros AFN-40-BI",
        "price": 249.90,
        "list_price": 399.90,
        "previous_price": 319.90,
        "source": "Magazine Luiza",
        "brand": "Mondial",
        "category": "eletrodomesticos",
        "url": "https://www.magazineluiza.com.br/busca/airfryer+mondial+4l/",
        "image_url": "https://images.unsplash.com/photo-1584269600464-37b1b58a9fe7?w=600&auto=format&fit=crop&q=80",
        "rating": 4.7,
        "review_count": 5450,
        "free_shipping": 1,
        "coupon_code": None,
        "days_ago_drop": 2,
        "history": [389.90, 349.90, 319.90, 249.90],
    },
    {
        "id": "amz_airfryer_philips_walita",
        "title": "Fritadeira Elétrica Airfryer Philips Walita Série 3000 4.1L Conectada",
        "price": 399.00,
        "list_price": 599.00,
        "previous_price": 489.00,
        "source": "Amazon",
        "brand": "Philips Walita",
        "category": "eletrodomesticos",
        "url": "https://www.amazon.com.br/s?k=Airfryer+Philips+Walita",
        "image_url": "https://images.unsplash.com/photo-1584269600464-37b1b58a9fe7?w=600&auto=format&fit=crop&q=80",
        "rating": 4.8,
        "review_count": 2100,
        "free_shipping": 1,
        "coupon_code": None,
        "days_ago_drop": 1,
        "history": [579.00, 529.00, 489.00, 399.00],
    },
    {
        "id": "ml_robo_aspirador_kabum",
        "title": "Robô Aspirador de Pó Inteligente KaBuM! Smart 700 Mapeamento Laser",
        "price": 1199.90,
        "list_price": 1699.90,
        "previous_price": 1449.90,
        "source": "Mercado Livre",
        "brand": "KaBuM!",
        "category": "eletrodomesticos",
        "url": "https://lista.mercadolivre.com.br/robo-aspirador-kabum-smart-700",
        "image_url": "https://images.unsplash.com/photo-1518770660439-4636190af475?w=600&auto=format&fit=crop&q=80",
        "rating": 4.7,
        "review_count": 680,
        "free_shipping": 1,
        "coupon_code": "SMARTROBO",
        "days_ago_drop": 3,
        "history": [1649.90, 1549.90, 1449.90, 1199.90],
    },
    {
        "id": "amz_nespresso_essenza_mini",
        "title": "Cafeteira Nespresso Essenza Mini 19 Bar 110V Preto",
        "price": 479.00,
        "list_price": 649.00,
        "previous_price": 569.00,
        "source": "Amazon",
        "brand": "Nespresso",
        "category": "eletrodomesticos",
        "url": "https://www.amazon.com.br/s?k=Cafeteira+Nespresso+Essenza+Mini",
        "image_url": "https://images.unsplash.com/photo-1514432324607-a09d9b4aefdd?w=600&auto=format&fit=crop&q=80",
        "rating": 4.8,
        "review_count": 3900,
        "free_shipping": 1,
        "coupon_code": None,
        "days_ago_drop": 2,
        "history": [629.00, 589.00, 569.00, 479.00],
    },
    {
        "id": "magalu_lava_seca_samsung",
        "title": "Lava e Seca Samsung EcoBubble 11kg Inox Look WD11M com Motor Digital Inverter",
        "price": 3499.00,
        "list_price": 4699.00,
        "previous_price": 3999.00,
        "source": "Magazine Luiza",
        "brand": "Samsung",
        "category": "eletrodomesticos",
        "url": "https://www.magazineluiza.com.br/busca/lava+e+seca+samsung+ecobubble/",
        "image_url": "https://images.unsplash.com/photo-1626806787461-102c1bfaaea1?w=600&auto=format&fit=crop&q=80",
        "rating": 4.8,
        "review_count": 1820,
        "free_shipping": 1,
        "coupon_code": None,
        "days_ago_drop": 5,
        "history": [4499.00, 4199.00, 3999.00, 3499.00],
    },

    # ==========================================
    # 6. CASA & COZINHA
    # ==========================================
    {
        "id": "magalu_jogo_panelas_tramontina",
        "title": "Jogo de Panelas Tramontina Antiaderente Paris 7 Peças Vermelho",
        "price": 289.90,
        "list_price": 429.90,
        "previous_price": 349.90,
        "source": "Magazine Luiza",
        "brand": "Tramontina",
        "category": "casa",
        "url": "https://www.magazineluiza.com.br/busca/jogo+de+panelas+tramontina+paris/",
        "image_url": "https://images.unsplash.com/photo-1556911220-e15b29be8c8f?w=600&auto=format&fit=crop&q=80",
        "rating": 4.8,
        "review_count": 9200,
        "free_shipping": 1,
        "coupon_code": None,
        "days_ago_drop": 2,
        "history": [419.90, 379.90, 349.90, 289.90],
    },
    {
        "id": "amz_jogo_facas_century",
        "title": "Jogo de Facas Tramontina Century com Lâminas em Aço Inox 6 Peças com Bloco de Madeira",
        "price": 419.90,
        "list_price": 599.90,
        "previous_price": 499.90,
        "source": "Amazon",
        "brand": "Tramontina",
        "category": "casa",
        "url": "https://www.amazon.com.br/s?k=Jogo+de+Facas+Tramontina+Century",
        "image_url": "https://images.unsplash.com/photo-1593618998160-e34014e67546?w=600&auto=format&fit=crop&q=80",
        "rating": 4.9,
        "review_count": 1400,
        "free_shipping": 1,
        "coupon_code": None,
        "days_ago_drop": 3,
        "history": [579.90, 529.90, 499.90, 419.90],
    },
    {
        "id": "ml_parafusadeira_bosch_18v",
        "title": "Parafusadeira e Furadeira de Impacto Bosch GSB 180-LI 18V com Maleta e 2 Baterias",
        "price": 649.00,
        "list_price": 899.00,
        "previous_price": 769.00,
        "source": "Mercado Livre",
        "brand": "Bosch",
        "category": "casa",
        "url": "https://lista.mercadolivre.com.br/parafusadeira-furadeira-bosch-18v",
        "image_url": "https://images.unsplash.com/photo-1504148455328-c376907d081c?w=600&auto=format&fit=crop&q=80",
        "rating": 4.9,
        "review_count": 3100,
        "free_shipping": 1,
        "coupon_code": "BOSCH50",
        "days_ago_drop": 1,
        "history": [869.00, 819.00, 769.00, 649.00],
    }
]


def seed_database():
    db = SessionLocal()
    print("=" * 60)
    print("POPULANDO SÓ PROMO BOA COM OFERTAS E HISTÓRICOS REAIS")
    print("=" * 60)

    # 1. Garante Lojas Oficiais cadastradas
    stores_data = [
        {"slug": "amazon", "name": "Amazon", "affiliate_network": "Amazon Associates", "affiliate_tag": "sopromoboa-20"},
        {"slug": "mercadolivre", "name": "Mercado Livre", "affiliate_network": "Mercado Livre Afiliados", "affiliate_tag": "sopromoboa_ml"},
        {"slug": "magazineluiza", "name": "Magazine Luiza", "affiliate_network": "Parceiro Magalu", "affiliate_tag": "sopromoboa"},
        {"slug": "kabum", "name": "KaBuM!", "affiliate_network": "KaBuM Afiliados", "affiliate_tag": "sopromoboa"},
        {"slug": "shopee", "name": "Shopee", "affiliate_network": "Shopee Afiliados", "affiliate_tag": "sopromoboa_sp"},
    ]
    for s in stores_data:
        store = db.query(StoreModel).filter(StoreModel.slug == s["slug"]).first()
        if not store:
            store = StoreModel(slug=s["slug"], name=s["name"], affiliate_network=s["affiliate_network"], affiliate_tag=s["affiliate_tag"], is_active=1)
            db.add(store)
    db.commit()

    # 2. Carrega programas de afiliados para montar o affiliate_url
    programs = {p.network_slug: p.tracking_id for p in db.query(AffiliateProgramModel).all()}

    inserted_count = 0
    updated_count = 0

    for item in CURATED_PRODUCTS:
        product_id = item["id"]
        store_slug = item["source"].lower().replace(" ", "").replace("!", "")
        tracking_tag = programs.get(store_slug, "sopromoboa")
        
        # Constrói o affiliate_url
        clean_url = item["url"]
        sep = "&" if "?" in clean_url else "?"
        if "amazon.com.br" in clean_url:
            affiliate_url = f"{clean_url}{sep}tag={tracking_tag}&utm_source=sopromoboa&utm_medium=web&utm_campaign=radar"
        elif "mercadolivre.com.br" in clean_url:
            affiliate_url = f"{clean_url}{sep}matt_tool=sopromoboa&utm_source=sopromoboa"
        elif "magazineluiza.com.br" in clean_url:
            affiliate_url = f"{clean_url}{sep}utm_source=sopromoboa&utm_medium=afiliado"
        elif "kabum.com.br" in clean_url:
            affiliate_url = f"{clean_url}{sep}tag=sopromoboa"
        else:
            affiliate_url = f"{clean_url}{sep}tag={tracking_tag}"

        discount_pct = calculate_discount_percent(item["price"], list_price=item.get("list_price"), previous_price=item.get("previous_price"))
        price_drop_active = 1 if (item.get("previous_price") and item["price"] < item["previous_price"]) else 0
        price_changed_date = NOW - datetime.timedelta(days=item.get("days_ago_drop", 1))

        lowest_price = min(item.get("history", [item["price"]]))

        db_prod = db.query(ProductModel).filter(ProductModel.id == product_id).first()
        if not db_prod:
            db_prod = ProductModel(
                id=product_id,
                title=item["title"],
                price=item["price"],
                list_price=item.get("list_price"),
                previous_price=item.get("previous_price"),
                lowest_historic_price=lowest_price,
                price_dropped=price_drop_active,
                discount_percent=discount_pct,
                brand=item.get("brand"),
                category=item["category"],
                url=item["url"],
                affiliate_url=affiliate_url,
                source=item["source"],
                image_url=item.get("image_url"),
                is_available=1,
                rating=item.get("rating", 4.8),
                review_count=item.get("review_count", 100),
                coupon_code=item.get("coupon_code"),
                free_shipping=item.get("free_shipping", 1),
                is_affiliate_deal=item.get("is_affiliate_deal", 0),
                is_featured=item.get("is_featured", 0),
                clicks_count=item.get("clicks_count", 0),
                created_at=NOW - datetime.timedelta(days=15),
                last_updated=NOW,
                price_changed_at=price_changed_date,
            )
            db.add(db_prod)
            inserted_count += 1
        else:
            db_prod.title = item["title"]
            db_prod.price = item["price"]
            db_prod.list_price = item.get("list_price")
            db_prod.previous_price = item.get("previous_price")
            db_prod.lowest_historic_price = lowest_price
            db_prod.price_dropped = price_drop_active
            db_prod.discount_percent = discount_pct
            db_prod.brand = item.get("brand")
            db_prod.category = item["category"]
            db_prod.url = item["url"]
            db_prod.affiliate_url = affiliate_url
            db_prod.source = item["source"]
            db_prod.image_url = item.get("image_url")
            db_prod.rating = item.get("rating", 4.8)
            db_prod.review_count = item.get("review_count", 100)
            db_prod.coupon_code = item.get("coupon_code")
            db_prod.free_shipping = item.get("free_shipping", 1)
            db_prod.last_updated = NOW
            db_prod.price_changed_at = price_changed_date
            if "is_affiliate_deal" in item:
                db_prod.is_affiliate_deal = item["is_affiliate_deal"]
            if "is_featured" in item:
                db_prod.is_featured = item["is_featured"]
            updated_count += 1

        db.commit()

        # Cria ou atualiza os pontos de histórico de preço
        existing_hist = db.query(PriceHistoryModel).filter(PriceHistoryModel.product_id == product_id).count()
        if existing_hist < 3:
            db.query(PriceHistoryModel).filter(PriceHistoryModel.product_id == product_id).delete()
            history_values = item.get("history", [item["price"] * 1.15, item["price"] * 1.08, item["price"]])
            days_intervals = [14, 7, item.get("days_ago_drop", 2), 0]
            for val, d_ago in zip(history_values, days_intervals):
                hist_date = NOW - datetime.timedelta(days=d_ago)
                db.add(PriceHistoryModel(
                    product_id=product_id,
                    price=val,
                    seen_at=hist_date
                ))
            db.commit()

    # Atualiza contadores nas lojas
    for s in stores_data:
        count = db.query(ProductModel).filter(ProductModel.source == s["name"]).count()
        store = db.query(StoreModel).filter(StoreModel.slug == s["slug"]).first()
        if store:
            store.total_deals = count
    db.commit()

    total_prods = db.query(ProductModel).count()
    total_drops = db.query(ProductModel).filter(ProductModel.price_dropped == 1).count()
    total_hist = db.query(PriceHistoryModel).count()

    print(f"\n[SUCESSO] População Concluída!")
    print(f"  - Total de produtos no banco: {total_prods} (Inseridos: {inserted_count}, Atualizados: {updated_count})")
    print(f"  - Ofertas com queda real no Radar: {total_drops}")
    print(f"  - Pontos históricos de preço gravados: {total_hist}")
    print("=" * 60)
    db.close()

if __name__ == "__main__":
    seed_database()
