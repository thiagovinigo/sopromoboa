"""Autenticação do painel administrativo: senha vinda do ambiente e token assinado com validade.

Sem ADMIN_PASSWORD configurada o admin fica desligado (falha fechada): não existe senha padrão.
O token é enviado no cabeçalho X-Admin-Token e protege as rotas listadas em is_protected().
"""
import hashlib
import hmac
import os
import time
from typing import Optional

from fastapi import Request
from fastapi.responses import JSONResponse

TOKEN_HEADER = "X-Admin-Token"
TOKEN_TTL_SECONDS = 12 * 3600

_PROTECTED_PREFIXES = ("/api/admin/", "/api/agent/", "/api/deals/lightning/")
_PROTECTED_EXACT = {
    "/api/affiliates",
    "/api/worker/run",
    "/api/worker/simulate-drop",
    "/api/worker/status",
}
_PUBLIC_EXACT = {"/api/admin/auth"}


def _admin_password() -> str:
    return os.getenv("ADMIN_PASSWORD", "")


def _signing_secret() -> bytes:
    return (os.getenv("ADMIN_TOKEN_SECRET") or _admin_password()).encode("utf-8")


def is_admin_configured() -> bool:
    return bool(_admin_password())


def check_password(candidate: str) -> bool:
    if not is_admin_configured():
        return False
    return hmac.compare_digest(candidate.encode("utf-8"), _admin_password().encode("utf-8"))


def _sign(expires_at: int) -> str:
    return hmac.new(_signing_secret(), f"admin:{expires_at}".encode("utf-8"), hashlib.sha256).hexdigest()


def create_admin_token(now: Optional[float] = None) -> str:
    issued_at = int(time.time() if now is None else now)
    expires_at = issued_at + TOKEN_TTL_SECONDS
    return f"{expires_at}.{_sign(expires_at)}"


def verify_admin_token(token: Optional[str], now: Optional[float] = None) -> bool:
    if not token or not is_admin_configured():
        return False
    parts = token.split(".")
    if len(parts) != 2 or not parts[0].isdigit():
        return False
    expires_at = int(parts[0])
    if expires_at < (time.time() if now is None else now):
        return False
    return hmac.compare_digest(parts[1], _sign(expires_at))


def is_protected(method: str, path: str) -> bool:
    if method == "OPTIONS" or path in _PUBLIC_EXACT:
        return False
    return path in _PROTECTED_EXACT or path.startswith(_PROTECTED_PREFIXES)


async def admin_guard(request: Request, call_next):
    """Middleware: exige token válido nas rotas administrativas; as demais seguem abertas."""
    if not is_protected(request.method, request.url.path):
        return await call_next(request)
    if not is_admin_configured():
        return JSONResponse({"detail": "Painel administrativo desativado."}, status_code=503)
    if not verify_admin_token(request.headers.get(TOKEN_HEADER)):
        return JSONResponse({"detail": "Não autorizado."}, status_code=401)
    return await call_next(request)
