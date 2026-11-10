"""Busca sem distinção de acento: "hermetico" deve achar "Hermético" e vice-versa."""
import pytest
from sqlalchemy import create_engine, event, func
from sqlalchemy.orm import sessionmaker

from database import Base, register_sqlite_functions
from models import ProductModel
from normalize import extract_search_tokens, score_search_match
from text_utils import fold_text


def test_fold_text_removes_accents_and_lowercases():
    assert fold_text("Pote HERMÉTICO de Vidro") == "pote hermetico de vidro"
    assert fold_text("Açaí c/ cafeína") == "acai c/ cafeina"
    assert fold_text("") == ""
    assert fold_text(None) == ""


@pytest.mark.parametrize("query", ["pote hermético", "pote hermetico", "POTE HERMÉTICO", "Pote Hermetico"])
def test_score_matches_regardless_of_accent_in_query(query):
    assert score_search_match("Pote Hermético de Vidro 640 ml", 25.9, query) is not None


@pytest.mark.parametrize("query", ["pote hermético", "pote hermetico"])
def test_score_matches_regardless_of_accent_in_title(query):
    assert score_search_match("Pote Hermetico de Vidro 640 ml", 25.9, query) is not None


def test_score_still_rejects_unrelated_title():
    assert score_search_match("Liquidificador 900W", 99.0, "pote hermetico") is None


def test_tokens_are_folded():
    assert extract_search_tokens("Pote Hermético") == ["pote", "hermetico"]


def test_sqlite_function_filters_ignoring_accents():
    engine = create_engine("sqlite://")
    event.listen(engine, "connect", lambda conn, _rec: register_sqlite_functions(conn))
    Base.metadata.create_all(engine)
    db = sessionmaker(bind=engine)()
    for i, title in enumerate(["Pote Hermético A", "Pote hermetico B", "Panela Inox"]):
        db.add(ProductModel(
            id=f"p{i}", title=title, price=10.0, url=f"https://x/{i}", affiliate_url=f"https://x/{i}",
            source="Shopee", image_url="https://img/x.jpg", is_available=1,
        ))
    db.commit()
    rows = db.query(ProductModel).filter(func.fold_text(ProductModel.title).like("%hermetico%")).all()
    assert sorted(r.title for r in rows) == ["Pote Hermético A", "Pote hermetico B"]
