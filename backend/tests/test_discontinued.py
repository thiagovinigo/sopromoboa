import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database import Base
from models import ProductModel
import scraper_worker as worker


@pytest.fixture
def db():
    engine = create_engine("sqlite://")
    Base.metadata.create_all(bind=engine)
    session = sessionmaker(bind=engine)()
    yield session
    session.close()


def add(db, product_id, url, affiliate_url=None, source="Loja"):
    db.add(
        ProductModel(
            id=product_id, title=product_id, price=10.0, url=url,
            affiliate_url=affiliate_url, source=source, is_available=1,
        )
    )


def available_ids(db):
    return sorted(p.id for p in db.query(ProductModel).filter(ProductModel.is_available == 1))


def test_discontinued_prefixes_and_third_party_links_are_retired(db):
    add(db, "ml_flagship", "https://www.mercadolivre.com.br/p/MLB1")  # fonte descontinuada
    add(db, "gatry_a", "https://meli.la/1fogrET")  # link curto do afiliado de terceiros
    add(db, "gatry_b", "https://www.amazon.com.br/dp/B1", "https://link.amazon/xyz")
    add(db, "gatry_c", "https://amzn.to/3abc")
    add(db, "gatry_ok", "https://www.amazon.com.br/dp/B2", "https://www.amazon.com.br/dp/B2?tag=thiagovinigo-20")
    add(db, "lmd_ok", "https://littleduck.com.br/p/1", "https://lmdee.link/abc")
    db.commit()

    retired = worker.retire_discontinued_items(db)

    assert retired == 4
    assert available_ids(db) == ["gatry_ok", "lmd_ok"]


def test_retire_discontinued_items_is_idempotent(db):
    add(db, "ml_x", "https://www.mercadolivre.com.br/p/MLB1")
    db.commit()

    assert worker.retire_discontinued_items(db) == 1
    assert worker.retire_discontinued_items(db) == 0


def test_missing_items_are_not_retired_when_the_batch_is_too_small(db):
    add(db, "gatry_1", "https://www.amazon.com.br/dp/B1")
    add(db, "gatry_2", "https://www.amazon.com.br/dp/B2")
    db.commit()

    few = [f"gatry_{i}" for i in range(5)]  # varredura quase vazia = provável falha da fonte
    assert worker.retire_missing_products(db, {"name": "Gatry"}, few) == 0

    many = [f"gatry_keep_{i}" for i in range(worker.MIN_ITEMS_TO_RETIRE)]
    assert worker.retire_missing_products(db, {"name": "Gatry"}, many) == 2
    db.commit()
    assert available_ids(db) == []
