from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.clients.deribit import DeribitClient


def mock_deribit_response(payload):
    response = MagicMock()
    response.__aenter__.return_value = response
    response.__aexit__.return_value = False
    response.raise_for_status = MagicMock()
    response.json = AsyncMock(return_value=payload)

    session = MagicMock()
    session.__aenter__.return_value = session
    session.__aexit__.return_value = False
    session.get.return_value = response

    return session


@pytest.mark.asyncio
async def test_get_index_price_success(monkeypatch):
    session = mock_deribit_response(
        {"result": {"index_price": 82646.1}}
    )
    monkeypatch.setattr(
        "app.clients.deribit.aiohttp.ClientSession",
        lambda **kwargs: session,
    )

    client = DeribitClient()
    price = await client.get_index_price("btc_usd")

    assert price == Decimal("82646.1")
    session.get.assert_called_once()


@pytest.mark.asyncio
async def test_get_index_price_missing_price(monkeypatch):
    session = mock_deribit_response({"result": {}})
    monkeypatch.setattr(
        "app.clients.deribit.aiohttp.ClientSession",
        lambda **kwargs: session,
    )

    client = DeribitClient()

    with pytest.raises(ValueError, match="Missing index price"):
        await client.get_index_price("btc_usd")


@pytest.mark.asyncio
async def test_get_index_price_api_error(monkeypatch):
    session = mock_deribit_response(
        {"error": {"message": "Invalid index"}}
    )
    monkeypatch.setattr(
        "app.clients.deribit.aiohttp.ClientSession",
        lambda **kwargs: session,
    )

    client = DeribitClient()

    with pytest.raises(RuntimeError, match="Deribit API error"):
        await client.get_index_price("btc_usd")
