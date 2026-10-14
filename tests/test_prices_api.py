from decimal import Decimal
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient

from app.api.routes import prices as prices_routes
from app.main import app


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def fake_price():
    return SimpleNamespace(
        id=1,
        ticker="btc_usd",
        price=Decimal("82646.10000000"),
        timestamp=1791983160021,
    )


def test_get_latest_price(client, fake_price, monkeypatch):
    class FakePriceService:
        def __init__(self, db):
            pass

        def get_latest(self, ticker):
            assert ticker == "btc_usd"
            return fake_price

    monkeypatch.setattr(
        prices_routes, "PriceService", FakePriceService
    )

    response = client.get(
        "/api/v1/prices/latest",
        params={"ticker": "btc_usd"},
    )

    assert response.status_code == 200
    assert response.json()["ticker"] == "btc_usd"
    assert response.json()["price"] == "82646.10000000"


def test_get_latest_price_not_found(client, monkeypatch):
    class FakePriceService:
        def __init__(self, db):
            pass

        def get_latest(self, ticker):
            return None

    monkeypatch.setattr(
        prices_routes, "PriceService", FakePriceService
    )

    response = client.get(
        "/api/v1/prices/latest",
        params={"ticker": "btc_usd"},
    )

    assert response.status_code == 404


def test_ticker_is_required(client):
    response = client.get("/api/v1/prices/latest")

    assert response.status_code == 422


def test_invalid_ticker(client):
    response = client.get(
        "/api/v1/prices/latest",
        params={"ticker": "doge_usd"},
    )

    assert response.status_code == 422


def test_get_prices_by_date(client, fake_price, monkeypatch):
    class FakePriceService:
        def __init__(self, db):
            pass

        def get_by_date(self, ticker, date):
            assert ticker == "btc_usd"
            return [fake_price]

    monkeypatch.setattr(
        prices_routes, "PriceService", FakePriceService
    )

    response = client.get(
        "/api/v1/prices/by-date",
        params={
            "ticker": "btc_usd",
            "date": "2026-10-14",
        },
    )

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["ticker"] == "btc_usd"