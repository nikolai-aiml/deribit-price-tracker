from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.services.price_service import PriceService


@pytest.mark.asyncio
async def test_collect_prices_saves_btc_and_eth(monkeypatch):
    client = MagicMock()
    client.get_index_price = AsyncMock(
        side_effect=[
            Decimal("82646.1"),
            Decimal("2650.5"),
        ]
    )

    service = PriceService(
        session=MagicMock(),
        client=client,
    )

    saved_records = []

    def save_price(ticker, price, timestamp):
        record = SimpleNamespace(
            ticker=ticker,
            price=price,
            timestamp=timestamp,
        )
        saved_records.append(record)
        return record

    monkeypatch.setattr(service.repository, "save", save_price)

    result = await service.collect_prices()

    assert [record["ticker"] for record in result] == [
        "btc_usd",
        "eth_usd",
    ]
    assert result[0]["price"] == Decimal("82646.1")
    assert result[1]["price"] == Decimal("2650.5")
    assert len(saved_records) == 2

    client.get_index_price.assert_any_await("btc_usd")
    client.get_index_price.assert_any_await("eth_usd")


@pytest.mark.asyncio
async def test_collect_prices_propagates_client_error(monkeypatch):
    client = MagicMock()
    client.get_index_price = AsyncMock(
        side_effect=RuntimeError("Deribit unavailable")
    )

    service = PriceService(
        session=MagicMock(),
        client=client,
    )

    save_mock = MagicMock()
    monkeypatch.setattr(service.repository, "save", save_mock)

    with pytest.raises(RuntimeError, match="Deribit unavailable"):
        await service.collect_prices()

    save_mock.assert_not_called()
