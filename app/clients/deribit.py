from decimal import Decimal

import aiohttp

from app.core.config import get_settings


class DeribitClient:
    def __init__(self, base_url: str | None = None) -> None:
        settings = get_settings()
        self.base_url = (base_url or settings.deribit_base_url).rstrip("/")

    async def get_index_price(self, ticker: str) -> Decimal:
        async with (
            aiohttp.ClientSession() as session,
            session.get(
                f"{self.base_url}/public/get_index_price",
                params={"index_name": ticker},
                timeout=aiohttp.ClientTimeout(total=15),
            ) as response,
        ):
            response.raise_for_status()
            payload = await response.json()

        if "error" in payload:
            raise RuntimeError(f"Deribit API error: {payload['error']}")

        result = payload.get("result")
        if not result or "index_price" not in result:
            raise ValueError(f"Missing index price for {ticker}")

        return Decimal(str(result["index_price"]))
