import datetime
from pricing import (
    apply_price_change,
    is_price_drop_active,
    calculate_discount_percent,
    is_all_time_low,
    DROP_WINDOW_DAYS
)


def test_first_price_seen():
    now = datetime.datetime.utcnow()
    res = apply_price_change(None, 1000.0, now)
    assert res["price"] == 1000.0
    assert res["lowest_historic_price"] == 1000.0


def test_price_drop_detected():
    now = datetime.datetime.utcnow()
    # Caiu de 1000 para 800 (20% de queda)
    res = apply_price_change(1000.0, 800.0, now, historic_lowest=1000.0)
    assert res["price"] == 800.0
    assert res["previous_price"] == 1000.0
    assert res["lowest_historic_price"] == 800.0


def test_minor_cent_noise_ignored():
    now = datetime.datetime.utcnow()
    # Variação de centavos (< 2%)
    res = apply_price_change(100.0, 99.50, now)
    assert res["price"] == 99.50
    assert "previous_price" not in res # Não deve registrar como queda promocional


def test_price_increase_clears_drop():
    now = datetime.datetime.utcnow()
    # Preço subiu de 800 para 950
    res = apply_price_change(800.0, 950.0, now)
    assert res["price"] == 950.0
    assert res["previous_price"] is None


def test_drop_window_expiry():
    now = datetime.datetime.utcnow()
    changed_6_days_ago = now - datetime.timedelta(days=6)
    changed_10_days_ago = now - datetime.timedelta(days=10)

    # Dentro da janela de 7 dias
    assert is_price_drop_active(800.0, 1000.0, changed_6_days_ago, now) is True

    # Fora da janela de 7 dias
    assert is_price_drop_active(800.0, 1000.0, changed_10_days_ago, now) is False


def test_discount_percent():
    assert calculate_discount_percent(80.0, list_price=100.0) == 20.0
    assert calculate_discount_percent(700.0, previous_price=1000.0) == 30.0
    assert calculate_discount_percent(100.0, list_price=100.0) == 0.0


def test_all_time_low():
    assert is_all_time_low(500.0, 500.0) is True
    assert is_all_time_low(490.0, 500.0) is True
    assert is_all_time_low(550.0, 500.0) is False


def test_no_all_time_low_without_price_history():
    assert is_all_time_low(59.0, None) is False


def test_lightning_flag_is_off_by_default():
    import feature_flags

    assert feature_flags.LIGHTNING_ENABLED is False
