"""Chaves de funcionalidades lidas do ambiente (desligadas por padrão)."""
import os

# Ofertas Relâmpago: desligadas até haver histórico de preço confiável para sustentar o selo.
LIGHTNING_ENABLED = os.getenv("LIGHTNING_ENABLED", "0") == "1"
