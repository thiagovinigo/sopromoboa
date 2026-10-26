"""Mercado Livre: desligado até haver uma fonte confiável.

A API de busca do Mercado Livre responde 403 para o nosso aplicativo (não certificado). As fontes antigas
foram retiradas porque enganavam: uma lista fixa de produtos com preço escrito à mão (nunca consultado no
site), "preço original" inventado (preço x 1,35) e links curtos do Gatry (meli.la), que mandavam a comissão
para o afiliado de outra pessoa.

Quando houver uma fonte real (API certificada, feed de afiliados), ela entra aqui, marcando os links com a
nossa tag (matt_tool) e usando o preço de lista informado pela loja.
"""
from typing import Any, Dict, List


def scrape_mercadolivre() -> List[Dict[str, Any]]:
    return []
