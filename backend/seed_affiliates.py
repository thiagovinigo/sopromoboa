"""Inicializa os programas de afiliados padrão no banco de dados."""
from database import SessionLocal
from models import AffiliateProgramModel

DEFAULTS = [
    {
        "name": "Amazon Brasil Associados",
        "network_slug": "amazon",
        "tracking_id": "sopromoboa-20",
        "commission_rate": "Até 15%",
        "status": "active"
    },
    {
        "name": "Parceiro Magalu (Magazine Luiza)",
        "network_slug": "magalu",
        "tracking_id": "sopromoboa",
        "commission_rate": "Até 12%",
        "status": "active"
    },
    {
        "name": "Mercado Livre Afiliados",
        "network_slug": "mercadolivre",
        "tracking_id": "sopromoboa_ml",
        "commission_rate": "Até 16%",
        "status": "active"
    },
    {
        "name": "KaBuM! Afiliados",
        "network_slug": "kabum",
        "tracking_id": "sopromoboa",
        "commission_rate": "Até 8%",
        "status": "active"
    },
    {
        "name": "Shopee Afiliados",
        "network_slug": "shopee",
        "tracking_id": "an_18356121277",
        "commission_rate": "Até 14% a 20%",
        "status": "active"
    },
    {
        "name": "Lomadee / SocialSoul (Magalu, KaBuM, Fast Shop)",
        "network_slug": "lomadee",
        "tracking_id": "sopromoboa_lomadee",
        "commission_rate": "Até 12%",
        "status": "active"
    }
]

def seed_affiliates():
    db = SessionLocal()
    try:
        count = 0
        for p in DEFAULTS:
            existing = db.query(AffiliateProgramModel).filter(AffiliateProgramModel.network_slug == p["network_slug"]).first()
            if not existing:
                db.add(AffiliateProgramModel(**p))
                count += 1
        db.commit()
        print(f"[Seed] {count} programas de afiliados cadastrados com sucesso!")
    finally:
        db.close()

if __name__ == "__main__":
    seed_affiliates()
