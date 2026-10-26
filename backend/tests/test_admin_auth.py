import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from starlette.middleware.base import BaseHTTPMiddleware

import admin_auth as aa

PASSWORD = "correct horse battery staple"


@pytest.fixture(autouse=True)
def configured_password(monkeypatch):
    monkeypatch.setenv("ADMIN_PASSWORD", PASSWORD)
    monkeypatch.delenv("ADMIN_TOKEN_SECRET", raising=False)


def test_check_password_accepts_only_the_configured_password():
    assert aa.check_password(PASSWORD) is True
    assert aa.check_password("wrong") is False
    assert aa.check_password("") is False


def test_admin_is_disabled_without_a_configured_password(monkeypatch):
    monkeypatch.delenv("ADMIN_PASSWORD")

    assert aa.is_admin_configured() is False
    assert aa.check_password(PASSWORD) is False
    assert aa.verify_admin_token(aa.create_admin_token()) is False


def test_token_roundtrip_and_expiry():
    token = aa.create_admin_token(now=1_000)

    assert aa.verify_admin_token(token, now=1_000 + 60) is True
    assert aa.verify_admin_token(token, now=1_000 + aa.TOKEN_TTL_SECONDS + 1) is False


@pytest.mark.parametrize("token", ["", "garbage", "123.abc", "abc.def.ghi", None])
def test_malformed_tokens_are_rejected(token):
    assert aa.verify_admin_token(token) is False


def test_tampered_or_foreign_tokens_are_rejected(monkeypatch):
    token = aa.create_admin_token(now=1_000)
    expires, signature = token.split(".")

    assert aa.verify_admin_token(f"{int(expires) + 999}.{signature}", now=1_000) is False

    monkeypatch.setenv("ADMIN_PASSWORD", "another password")
    assert aa.verify_admin_token(token, now=1_000) is False


@pytest.mark.parametrize(
    "method,path,expected",
    [
        ("GET", "/api/admin/stats", True),
        ("DELETE", "/api/admin/deals/abc", True),
        ("POST", "/api/admin/auth", False),
        ("GET", "/api/affiliates", True),
        ("POST", "/api/affiliates", True),
        ("POST", "/api/affiliates/generate", False),
        ("POST", "/api/worker/run", True),
        ("POST", "/api/worker/simulate-drop", True),
        ("GET", "/api/worker/status", True),
        ("GET", "/api/worker/search", False),
        ("POST", "/api/deals/lightning/robot-run", True),
        ("POST", "/api/deals/lightning/scan", True),
        ("GET", "/api/agent/hunter/stores", True),
        ("POST", "/api/agent/hunter/stores/1/approve", True),
        ("GET", "/api/deals", False),
        ("GET", "/api/health", False),
        ("GET", "/r/abc", False),
        ("OPTIONS", "/api/admin/stats", False),
    ],
)
def test_is_protected(method, path, expected):
    assert aa.is_protected(method, path) is expected


@pytest.fixture
def client():
    app = FastAPI()
    app.add_middleware(BaseHTTPMiddleware, dispatch=aa.admin_guard)

    @app.get("/api/admin/stats")
    def stats():
        return {"ok": True}

    @app.get("/api/deals")
    def deals():
        return []

    return TestClient(app)


def test_guard_blocks_protected_routes_without_a_token(client):
    assert client.get("/api/admin/stats").status_code == 401


def test_guard_blocks_a_bad_token(client):
    assert client.get("/api/admin/stats", headers={aa.TOKEN_HEADER: "nope"}).status_code == 401


def test_guard_allows_a_valid_token(client):
    headers = {aa.TOKEN_HEADER: aa.create_admin_token()}

    assert client.get("/api/admin/stats", headers=headers).status_code == 200


def test_guard_leaves_public_routes_open(client):
    assert client.get("/api/deals").status_code == 200


def test_guard_fails_closed_when_admin_is_not_configured(client, monkeypatch):
    monkeypatch.delenv("ADMIN_PASSWORD")

    assert client.get("/api/admin/stats").status_code == 503
    assert client.get("/api/deals").status_code == 200
