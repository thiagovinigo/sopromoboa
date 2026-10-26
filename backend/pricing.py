"""Regras de negócio de preço, detecção de queda e histórico de promoções.

Funções puras utilizadas tanto pelo scraper_worker (ao persistir dados)
quanto pela API (ao consultar e filtrar produtos).
"""
import datetime
from typing import Optional, Dict, Any

# Janela em dias para considerar uma queda de preço como "Promoção Ativa"
DROP_WINDOW_DAYS = 7

# Variação mínima para ser considerada queda real (ignora oscilações de centavos)
MIN_DROP_PERCENT = 2.0


def apply_price_change(
    old_price: Optional[float],
    new_price: float,
    now: datetime.datetime,
    historic_lowest: Optional[float] = None
) -> Dict[str, Any]:
    """Calcula os campos atualizados quando o preço de um produto sofre alteração.

    - Preço inválido ou idêntico: não altera nada.
    - Primeiro preço visto: define preço atual e menor histórico.
    - Queda de preço relevante: registra previous_price e timestamp da queda.
    - Queda ínfima (< 2%): apenas atualiza o preço para não poluir o radar.
    - Aumento de preço: atualiza o preço e limpa o status de queda recente.
    """
    if new_price is None or new_price <= 0:
        return {}

    if old_price is None or old_price <= 0:
        return {
            "price": new_price,
            "lowest_historic_price": new_price,
            "price_changed_at": now,
        }

    if abs(new_price - old_price) < 0.01:
        return {}

    updates: Dict[str, Any] = {"price": new_price, "price_changed_at": now}

    # Atualiza menor preço histórico se bateu recorde
    current_lowest = historic_lowest if (historic_lowest and historic_lowest > 0) else old_price
    if new_price < current_lowest:
        updates["lowest_historic_price"] = new_price

    if new_price > old_price:
        # Preço subiu: limpa a marcação de queda ativa
        updates["previous_price"] = None
        return updates

    # Preço caiu
    drop_pct = (old_price - new_price) / old_price * 100.0
    if drop_pct >= MIN_DROP_PERCENT:
        updates["previous_price"] = old_price
    else:
        # Variação irrelevante (ruído de centavos)
        pass

    return updates


def is_price_drop_active(
    price: float,
    previous_price: Optional[float],
    changed_at: Optional[datetime.datetime],
    now: datetime.datetime,
    window_days: int = DROP_WINDOW_DAYS
) -> bool:
    """Retorna True se o item teve uma queda real de preço dentro da janela de dias."""
    if not previous_price or changed_at is None or price >= previous_price:
        return False
    return (now - changed_at) <= datetime.timedelta(days=window_days)


def calculate_discount_percent(
    price: float,
    list_price: Optional[float] = None,
    previous_price: Optional[float] = None
) -> float:
    """Calcula o maior percentual de desconto real disponível.
    
    Usa list_price (preço 'de') ou previous_price (preço anterior à queda).
    """
    reference = None
    if list_price and list_price > price:
        reference = list_price
    elif previous_price and previous_price > price:
        reference = previous_price

    if not reference or reference <= 0:
        return 0.0

    return round(((reference - price) / reference) * 100.0, 1)


def is_all_time_low(price: float, lowest_historic_price: Optional[float]) -> bool:
    """Retorna True se o preço atual é igual ou menor ao menor preço histórico registrado.

    Sem histórico registrado não há como afirmar "menor preço": retorna False.
    """
    if not lowest_historic_price or lowest_historic_price <= 0:
        return False
    return price <= (lowest_historic_price + 0.05)
