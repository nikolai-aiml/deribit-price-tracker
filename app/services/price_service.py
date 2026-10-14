import time

from sqlalchemy.orm import Session

from app.clients.deribit import DeribitClient
from app.repositories.price_repository import PriceRepository

SUPPORTED_TICKERS = ("btc_usd", "eth_usd")


class PriceService:
    def __init__(
        self,
        session: Session,
        client: DeribitClient | None = None,
    ) -> None:
        self.repository = PriceRepository(session)
        self.client = client or DeribitClient()

    async def collect_prices(self) -> list[dict]:
        timestamp = time.time_ns() // 1_000_000
        saved = []

        for ticker in SUPPORTED_TICKERS:
            price = await self.client.get_index_price(ticker)
            record = self.repository.save(
                ticker=ticker,
                price=price,
                timestamp=timestamp,
            )
            saved.append(
                {
                    "ticker": record.ticker,
                    "price": record.price,
                    "timestamp": record.timestamp,
                }
            )

        return saved

    def get_all(self, ticker: str):
        return self.repository.get_all(ticker)

    def get_latest(self, ticker: str):
        return self.repository.get_latest(ticker)

    def get_by_date(self, ticker: str, date):
        return self.repository.get_by_date(ticker, date)
