from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import PriceHistory


class PriceRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_all(self, ticker: str) -> list[PriceHistory]:
        statement = (
            select(PriceHistory)
            .where(PriceHistory.ticker == ticker)
            .order_by(PriceHistory.timestamp.desc())
        )
        return list(self.session.scalars(statement).all())

    def get_latest(self, ticker: str) -> PriceHistory | None:
        statement = (
            select(PriceHistory)
            .where(PriceHistory.ticker == ticker)
            .order_by(PriceHistory.timestamp.desc())
            .limit(1)
        )
        return self.session.scalar(statement)

    def get_by_date(
        self,
        ticker: str,
        date: datetime,
    ) -> list[PriceHistory]:
        start = int(
            date.replace(hour=0, minute=0, second=0, microsecond=0).timestamp() * 1000
        )
        end = start + 86_400_000

        statement = (
            select(PriceHistory)
            .where(
                PriceHistory.ticker == ticker,
                PriceHistory.timestamp >= start,
                PriceHistory.timestamp < end,
            )
            .order_by(PriceHistory.timestamp.asc())
        )
        return list(self.session.scalars(statement).all())

    def save(self, ticker: str, price, timestamp: int) -> PriceHistory:
        record = PriceHistory(
            ticker=ticker,
            price=price,
            timestamp=timestamp,
        )
        self.session.add(record)
        self.session.commit()
        self.session.refresh(record)
        return record
