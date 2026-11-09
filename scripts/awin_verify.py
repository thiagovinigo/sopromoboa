"""Confere os IDs de anunciante (awinmid) das lojas da Awin sem precisar do painel.

Para cada loja de AWIN_STORES, segue o link awin1.com/cread.php e checa se o redirecionamento termina no domínio
da loja. ID errado cai em outra loja ou numa página de erro da Awin. Rodar de uma máquina com acesso normal à internet:

    cd backend && python ../scripts/awin_verify.py

Para corrigir um ID sem mexer no código: AWIN_MID_<LOJA>=<id> no backend/.env.
"""
import sys
from pathlib import Path
from urllib.parse import urlparse

import requests

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))
from affiliate import AWIN_STORES, awin_mid, build_awin_url  # noqa: E402

TIMEOUT_SECONDS = 20
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}


def check_store(slug: str, cfg: dict) -> str:
    link = build_awin_url(f"https://www.{cfg['domain']}/", merchant_id=awin_mid(slug), clickref="verify")
    try:
        resp = requests.get(link, headers=HEADERS, timeout=TIMEOUT_SECONDS, allow_redirects=True)
    except requests.RequestException as exc:
        return f"ERRO   {slug:<11} mid={awin_mid(slug)}  {type(exc).__name__}"
    final_host = urlparse(resp.url).netloc.lower()
    ok = final_host == cfg["domain"] or final_host.endswith("." + cfg["domain"])
    status = "OK    " if ok else "FALHOU"
    return f"{status} {slug:<11} mid={awin_mid(slug)}  -> {final_host} ({resp.status_code})"


def main() -> int:
    results = [check_store(slug, cfg) for slug, cfg in AWIN_STORES.items()]
    print("\n".join(results))
    return 0 if all(line.startswith("OK") for line in results) else 1


if __name__ == "__main__":
    sys.exit(main())
