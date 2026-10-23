"""Robô Autônomo de Ofertas Relâmpago do Que Promo.

Opera de forma 100% autônoma, sem necessidade de ações manuais:
1. POPULAR: Rastrea novos produtos com desconto real na Amazon, Magalu, Mercado Livre e KaBuM.
2. ATUALIZAR: Recalcula descontos em tempo real, mantendo os nichos que mais faturam no topo.
3. EXCLUIR: Remove da vitrine de Ofertas Relâmpago os produtos cujo desconto caiu (<18%), cujo preço subiu ou que esgotaram.
4. AFILIADO: Garante que 100% dos links da Amazon usem o StoreID oficial 'thiagovinigo-20'.
"""
import os
import sys
import time
import re
from datetime import datetime, timedelta
from typing import Dict, Any

from database import SessionLocal
from models import ProductModel, PriceHistoryModel, AffiliateProgramModel
from scraper_worker import run_worker_once

# Estado global do robô autônomo acessível via API
robot_status = {
    "is_running": False,
    "last_run": None,
    "next_run": None,
    "total_active_lightning": 0,
    "last_stats": {
        "scraped": 0,
        "promoted": 0,
        "pruned": 0,
        "duration_seconds": 0
    },
    "history": []
}

AMAZON_STORE_ID = "thiagovinigo-20"


def enforce_amazon_affiliate_tag(db):
    """Garante que todos os produtos da Amazon no banco usem a tag oficial thiagovinigo-20."""
    try:
        amazon_prods = db.query(ProductModel).filter(
            ProductModel.source.ilike("%amazon%")
        ).all()
        for p in amazon_prods:
            target = p.affiliate_url or p.url
            if target and "amazon.com.br" in target:
                if "tag=" in target:
                    p.affiliate_url = re.sub(r"tag=[^&]+", f"tag={AMAZON_STORE_ID}", target)
                else:
                    sep = "&" if "?" in target else "?"
                    p.affiliate_url = f"{target}{sep}tag={AMAZON_STORE_ID}"
        db.commit()
    except Exception as e:
        print(f"[Robô Autônomo] Erro ao injetar tags Amazon: {e}")
        db.rollback()


def prune_expired_lightning_deals(db) -> int:
    """Exclui / desativa da vitrine de Ofertas Relâmpago os itens que perderam o desconto ou expiraram."""
    now = datetime.utcnow()
    stale_threshold = now - timedelta(days=3) # Ofertas com mais de 72h sem revalidação

    pruned_count = 0

    # 1. Remove ofertas relâmpago cujo preço subiu e o desconto caiu para menos de 18%
    subiu_preco = db.query(ProductModel).filter(
        ProductModel.is_lightning_deal == 1,
        ProductModel.discount_percent < 18.0,
        ProductModel.is_featured == 0
    ).all()
    for p in subiu_preco:
        p.is_lightning_deal = 0
        pruned_count += 1

    # 2. Remove ofertas relâmpago esgotadas ou indisponíveis
    esgotados = db.query(ProductModel).filter(
        ProductModel.is_lightning_deal == 1,
        ProductModel.is_available == 0
    ).all()
    for p in esgotados:
        p.is_lightning_deal = 0
        pruned_count += 1

    # 3. Remove ofertas antigas sem confirmação recente dos scrapers
    antigas = db.query(ProductModel).filter(
        ProductModel.is_lightning_deal == 1,
        ProductModel.last_updated < stale_threshold,
        ProductModel.is_featured == 0
    ).all()
    for p in antigas:
        p.is_lightning_deal = 0
        pruned_count += 1

    db.commit()
    return pruned_count


def promote_super_discounts_to_lightning(db) -> int:
    """Promove automaticamente para Ofertas Relâmpago os produtos com desconto >= 25% e flagships."""
    promoted_count = 0

    # 1. Itens disponíveis com desconto real >= 25%
    super_descontos = db.query(ProductModel).filter(
        ProductModel.is_available == 1,
        ProductModel.discount_percent >= 25.0,
        ProductModel.is_lightning_deal == 0
    ).all()
    for p in super_descontos:
        p.is_lightning_deal = 1
        promoted_count += 1

    # 2. Flagships dos nichos de maior faturamento com desconto >= 15%
    flagships_terms = [
        "fire tv", "echo dot", "echo pop", "kindle", "creatina creapure",
        "whey", "air fryer", "iphone 15", "galaxy s24", "jbl"
    ]
    for term in flagships_terms:
        matches = db.query(ProductModel).filter(
            ProductModel.is_available == 1,
            ProductModel.title.ilike(f"%{term}%"),
            ProductModel.discount_percent >= 15.0,
            ProductModel.is_lightning_deal == 0
        ).all()
        for p in matches:
            p.is_lightning_deal = 1
            promoted_count += 1

    db.commit()
    return promoted_count


def run_lightning_robot_cycle() -> Dict[str, Any]:
    """Executa um ciclo completo de automação:
    - Popula rodando os scrapers em background
    - Atualiza os preços e promove novos super descontos
    - Exclui ofertas expiradas e esgotadas
    - Assegura tag thiagovinigo-20
    """
    if robot_status["is_running"]:
        return {"status": "busy", "message": "Robô já está em execução neste instante."}

    robot_status["is_running"] = True
    start_t = time.time()
    now_iso = datetime.utcnow().isoformat()
    db = SessionLocal()

    try:
        print("\n=======================================================")
        print("🤖 [ROBÔ AUTÔNOMO 1 HORA] Iniciando ciclo de varredura...")
        print("=======================================================")

        # 1. Executa scrapers para ler novidades da Amazon, Gatry e outras lojas
        worker_stats = run_worker_once()

        # 2. Injeta tags de afiliado da Amazon
        enforce_amazon_affiliate_tag(db)

        # 3. Exclui da vitrine itens que perderam o desconto ou expiraram
        pruned = prune_expired_lightning_deals(db)

        # 4. Promove novos super descontos para Ofertas Relâmpago
        promoted = promote_super_discounts_to_lightning(db)

        # 5. Contagem total de ofertas relâmpago ativas
        total_active = db.query(ProductModel).filter(
            ProductModel.is_lightning_deal == 1,
            ProductModel.is_available == 1
        ).count()

        duration = round(time.time() - start_t, 2)
        next_run_iso = (datetime.utcnow() + timedelta(hours=1)).isoformat()

        stats = {
            "scraped": worker_stats.get("inserted", 0) + worker_stats.get("updated", 0),
            "promoted": promoted,
            "pruned": pruned,
            "total_active": total_active,
            "duration_seconds": duration,
        }

        robot_status["last_run"] = now_iso
        robot_status["next_run"] = next_run_iso
        robot_status["total_active_lightning"] = total_active
        robot_status["last_stats"] = stats
        robot_status["history"].insert(0, {
            "timestamp": now_iso,
            "stats": stats,
            "duration": duration
        })
        robot_status["history"] = robot_status["history"][:20]

        print(f"🤖 [ROBÔ CONCLUÍDO em {duration}s]")
        print(f"Novas promoções: {promoted} | Expiradas removidas: {pruned} | Ativas: {total_active}\n")

        return {
            "success": True,
            "message": f"Varredura autônoma concluída: {promoted} itens promovidos, {pruned} expirados excluídos. Total ativo: {total_active}.",
            "stats": stats,
            "last_run": now_iso,
            "next_run": next_run_iso
        }
    except Exception as e:
        print(f"[Robô Autônomo] Erro durante o ciclo: {e}")
        return {"success": False, "error": str(e)}
    finally:
        db.close()
        robot_status["is_running"] = False


if __name__ == "__main__":
    result = run_lightning_robot_cycle()
    print("Resultado CLI:", result)
