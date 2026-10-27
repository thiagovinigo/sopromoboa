from datetime import datetime, timedelta

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import main
from database import Base, get_db
from models import ClickModel, ProductModel


@pytest.fixture
def client():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)

    def override():
        session = Session()
        try:
            yield session
        finally:
            session.close()

    main.app.dependency_overrides[get_db] = override
    seed = Session()
    yield TestClient(main.app), seed
    seed.close()
    main.app.dependency_overrides.pop(get_db, None)


def add_product(db, product_id, available=1):
    db.add(
        ProductModel(
            id=product_id, title=f"Produto {product_id}", price=10.0, url="https://loja.example/p",
            source="Amazon", category="geral", is_available=available, discount_percent=0.0,
        )
    )


def add_clicks(db, product_id, count, days_ago=0):
    for _ in range(count):
        db.add(ClickModel(product_id=product_id, source="Amazon", created_at=datetime.utcnow() - timedelta(days=days_ago)))


def test_popular_ranks_by_clicks_in_the_window_and_skips_unavailable_products(client):
    http, db = client
    for product_id in ("a", "b", "c", "d"):
        add_product(db, product_id, available=0 if product_id == "d" else 1)
    add_clicks(db, "a", 3)
    add_clicks(db, "b", 1)
    add_clicks(db, "c", 9, days_ago=20)  # fora da janela de 7 dias
    add_clicks(db, "d", 8)  # indisponível
    db.commit()

    response = http.get("/api/deals/popular?days=7")

    assert response.status_code == 200
    assert [deal["id"] for deal in response.json()] == ["a", "b"]


def test_popular_respects_the_limit_and_returns_empty_without_clicks(client):
    http, db = client
    for product_id in ("a", "b", "c"):
        add_product(db, product_id)
        add_clicks(db, product_id, 2)
    db.commit()

    assert len(http.get("/api/deals/popular?limit=2").json()) == 2

    db.query(ClickModel).delete()
    db.commit()
    assert http.get("/api/deals/popular").json() == []


def test_popular_route_is_not_swallowed_by_the_product_detail_route(client):
    http, _ = client

    assert http.get("/api/deals/popular").status_code == 200
