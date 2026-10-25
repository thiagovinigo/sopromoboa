"""Módulo de Notificação Automática para Canais do Telegram.

Envia ofertas relâmpago, bugs de preço e maiores quedas diretamente para
canais do Telegram com links de afiliados e formatação atrativa.
Zero risco de ban de número (usa a API oficial de bots do Telegram).
"""

import os
import requests
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger("telegram_notifier")

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL_ID", "")  # ex: @quepromo ou -100xxxxxxxxxx


def send_deal_to_telegram(
    title: str,
    price: float,
    previous_price: Optional[float] = None,
    list_price: Optional[float] = None,
    discount_percent: float = 0.0,
    store_name: str = "Loja Parceira",
    affiliate_url: str = "https://quepromo.com.br",
    coupon_code: Optional[str] = None,
    is_lightning: bool = False
) -> bool:
    """Envia uma oferta formatada para o canal oficial do Telegram."""
    token = os.getenv("TELEGRAM_BOT_TOKEN", TELEGRAM_BOT_TOKEN)
    channel = os.getenv("TELEGRAM_CHANNEL_ID", TELEGRAM_CHANNEL_ID)

    if not token or not channel:
        logger.debug("[Telegram] Token ou Channel ID não configurados no .env. Pulando envio.")
        return False

    api_url = f"https://api.telegram.org/bot{token}/sendMessage"

    # Emoji de cabeçalho
    header_emoji = "⚡ OFERTA RELÂMPAGO!" if is_lightning else "🔥 SUPER QUEDA DE PREÇO!"
    
    price_formatted = f"R$ {price:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    
    old_price_line = ""
    ref_old = previous_price or list_price
    if ref_old and ref_old > price:
        old_formatted = f"R$ {ref_old:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        old_price_line = f"❌ De: ~{old_formatted}~\n"

    discount_line = f"📉 Desconto: *{int(discount_percent)}% OFF*\n" if discount_percent > 0 else ""
    coupon_line = f"🎟 Cupom: `{coupon_code}`\n" if coupon_code else ""

    message_text = (
        f"*{header_emoji}*\n\n"
        f"*{title}*\n\n"
        f"{old_price_line}"
        f"✅ *Por: {price_formatted}*\n"
        f"{discount_line}"
        f"{coupon_line}"
        f"🏪 Loja: *{store_name}*\n\n"
        f"👉 [VER PROMOÇÃO COM DESCONTO]({affiliate_url})\n\n"
        f"🌐 Monitorado por: [quepromo.com.br](https://quepromo.com.br)"
    )

    payload = {
        "chat_id": channel,
        "text": message_text,
        "parse_mode": "Markdown",
        "disable_web_page_preview": False
    }

    try:
        resp = requests.post(api_url, json=payload, timeout=8)
        if resp.status_code == 200:
            logger.info(f"[Telegram] Oferta enviada com sucesso: {title[:40]}")
            return True
        else:
            logger.warning(f"[Telegram] Erro ao enviar mensagem ({resp.status_code}): {resp.text}")
            return False
    except Exception as e:
        logger.error(f"[Telegram] Exceção ao enviar para Telegram: {e}")
        return False
