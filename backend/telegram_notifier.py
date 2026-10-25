"""Módulo de Notificação Automática para Canais do Telegram - Padrão Alta Conversão.

Gera anúncios com foto, título chamativo, micro-copy persuasiva de benefício/dor,
ancoragem de preço com desconto calculado e botão interativo (Inline Keyboard).
Baseado no modelo campeão de afiliados (estilo WD-40 / Achadinhos).
"""

import os
import requests
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger("telegram_notifier")

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL_ID", "")  # ex: @quepromo ou -100xxxxxxxxxx


def generate_persuasive_pitch(title: str, category: str = "geral") -> str:
    """Gera uma micro-copy persuasiva de 2 frases focada em resolver um problema real,

    no estilo do anúncio de alta conversão.
    """
    t_lower = title.lower()

    if any(k in t_lower for k in ["fone", "earphone", "headset", "airpod", "bluetooth", "tws"]):
        return (
            "Som limpo com graves potentes e conexão estável para ouvir suas músicas "
            "e chamadas sem fios atrapalhando. Bateria de longa duração para treinar, "
            "trabalhar ou relaxar o dia todo. 🎧"
        )

    if any(k in t_lower for k in ["cortador", "maquina de cortar", "barbeador", "shaver", "aparador", "t9"]):
        return (
            "Lâminas afiadas de precisão que cortam rente à pele sem puxar nem irritar. "
            "Bateria recarregável de longa autonomia para manter o visual alinhado "
            "em poucos minutos em casa. ✂️"
        )

    if any(k in t_lower for k in ["refletor", "holofote", "led", "lampada", "luminaria", "ring light"]):
        return (
            "Iluminação forte de alta intensidade com máxima economia na conta de luz. "
            "Excelente durabilidade e resistência contra chuva e poeira para iluminar "
            "quintais, fachadas, estúdios ou garagens. 💡"
        )

    if any(k in t_lower for k in ["wd-40", "wd40", "desengripa", "lubrific", "ferramenta", "chave", "alicate", "furadeira", "parafusadeira"]):
        return (
            "O jato penetra fundo nas peças para soltar parafusos travados e eliminar "
            "rangidos metálicos incômodos. Protege contra ferrugem e umidade, sendo "
            "essencial na manutenção da casa e do carro. 🛠️"
        )

    if any(k in t_lower for k in ["air fryer", "fritadeira", "cafeteira", "panela", "liquidificador", "mixer", "cooktop"]):
        return (
            "Praticidade total na cozinha: prepare suas receitas favoritas crocantes e macias "
            "em minutos sem fazer sujeira de óleo. Economiza tempo na rotina e deixa sua "
            "alimentação muito mais saudável. 🍳"
        )

    if any(k in t_lower for k in ["smartwatch", "relogio", "smartband", "pulseira"]):
        return (
            "Monitore batimentos cardíacos, passos, queima de calorias e veja notificações "
            "do WhatsApp direto no pulso. Design moderno e bateria feita para durar a "
            "semana inteira de treinos e correria. ⌚"
        )

    if any(k in t_lower for k in ["creatina", "whey", "proteina", "suplemento", "pre-treino"]):
        return (
            "Pureza e rápida absorção para acelerar o ganho de força e explosão nos treinos. "
            "Ideal para quem busca bater metas de hipertrofia com o melhor custo-benefício. 💪"
        )

    if any(k in t_lower for k in ["ssd", "nvme", "memoria", "rtx", "monitor", "teclado", "mouse", "gamer"]):
        return (
            "Velocidade absurda e tempo de resposta imediato para acabar com travamentos "
            "e telas de carregamento. Mais fluidez para jogar em alto nível e produzir muito mais. ⚡"
        )

    if any(k in t_lower for k in ["extensao", "tomada", "carregador", "cabo"]):
        return (
            "Organize todos os seus aparelhos em um só lugar com proteção contra picos de "
            "tensão e curto-circuito. Carregue celulares e ligue eletrônicos com total segurança. 🔌"
        )

    # Fallback inteligente
    return (
        "Qualidade comprovada para resolver sua rotina com eficiência e durabilidade. "
        "Excelente custo-benefício para aproveitar enquanto o estoque promocional durar. ✨"
    )


def format_deal_post(
    title: str,
    price: float,
    previous_price: Optional[float] = None,
    list_price: Optional[float] = None,
    discount_percent: float = 0.0,
    store_name: str = "Loja Parceira",
    affiliate_url: str = "https://quepromo.com.br",
    coupon_code: Optional[str] = None,
    free_shipping: bool = False,
    category: str = "geral"
) -> Dict[str, Any]:
    """Formata o post completo do Telegram no modelo campeão de cliques."""
    # Preços formatados
    price_str = f"{price:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    ref_old = previous_price or list_price

    # Linha De: (riscado)
    old_price_line = ""
    if ref_old and ref_old > price:
        old_str = f"{ref_old:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        old_price_line = f"De: ~R$ {old_str}~\n"

    # Desconto
    calc_discount = discount_percent
    if not calc_discount and ref_old and ref_old > price:
        calc_discount = round(((ref_old - price) / ref_old) * 100)
    discount_line = f"🤑 Desconto de *{int(calc_discount)}%*\n" if calc_discount > 0 else ""

    # Cupom
    coupon_line = f"🎟 Cupom: `{coupon_code}`\n" if coupon_code else ""

    # Frete
    shipping_line = "🚚 *Frete Grátis* disponível\n" if free_shipping else ""

    # Pitch de benefício/dor
    pitch = generate_persuasive_pitch(title, category)

    caption = (
        f"*{title}*\n\n"
        f"_{pitch}_\n\n"
        f"{old_price_line}"
        f"💥 *Por: R$ {price_str}*\n"
        f"{discount_line}"
        f"{coupon_line}"
        f"{shipping_line}\n"
        f"🛒 *COMPRE AQUI* 👇\n"
        f"{affiliate_url}"
    )

    # Teclado interativo com botão nativo de compra
    reply_markup = {
        "inline_keyboard": [
            [
                {"text": "🛒 COMPRE AQUI COM DESCONTO", "url": affiliate_url}
            ],
            [
                {"text": "🔥 Mais Ofertas no Que Promo", "url": "https://quepromo.com.br"}
            ]
        ]
    }

    return {
        "caption": caption,
        "reply_markup": reply_markup,
        "pitch": pitch,
        "price_str": price_str
    }


def send_deal_to_telegram(
    title: str,
    price: float,
    previous_price: Optional[float] = None,
    list_price: Optional[float] = None,
    discount_percent: float = 0.0,
    store_name: str = "Loja Parceira",
    affiliate_url: str = "https://quepromo.com.br",
    image_url: Optional[str] = None,
    coupon_code: Optional[str] = None,
    free_shipping: bool = False,
    category: str = "geral"
) -> bool:
    """Envia a oferta formatada com foto e botão interativo para o canal do Telegram."""
    token = os.getenv("TELEGRAM_BOT_TOKEN", TELEGRAM_BOT_TOKEN)
    channel = os.getenv("TELEGRAM_CHANNEL_ID", TELEGRAM_CHANNEL_ID)

    if not token or not channel:
        logger.debug("[Telegram] Token ou Channel ID não configurados no .env. Pulando envio.")
        return False

    post = format_deal_post(
        title=title,
        price=price,
        previous_price=previous_price,
        list_price=list_price,
        discount_percent=discount_percent,
        store_name=store_name,
        affiliate_url=affiliate_url,
        coupon_code=coupon_code,
        free_shipping=free_shipping,
        category=category
    )

    # Se houver imagem válida, usa sendPhoto (fica igual ao print do WD-40)
    if image_url and image_url.startswith("http"):
        api_url = f"https://api.telegram.org/bot{token}/sendPhoto"
        payload = {
            "chat_id": channel,
            "photo": image_url,
            "caption": post["caption"],
            "parse_mode": "Markdown",
            "reply_markup": post["reply_markup"]
        }
    else:
        api_url = f"https://api.telegram.org/bot{token}/sendMessage"
        payload = {
            "chat_id": channel,
            "text": post["caption"],
            "parse_mode": "Markdown",
            "reply_markup": post["reply_markup"],
            "disable_web_page_preview": False
        }

    try:
        resp = requests.post(api_url, json=payload, timeout=10)
        if resp.status_code == 200:
            logger.info(f"[Telegram] Oferta enviada com sucesso: {title[:40]}")
            return True
        else:
            logger.warning(f"[Telegram] Erro ao enviar para Telegram ({resp.status_code}): {resp.text}")
            return False
    except Exception as e:
        logger.error(f"[Telegram] Exceção ao enviar para Telegram: {e}")
        return False
