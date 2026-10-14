from decimal import Decimal

from sqlalchemy import BigInteger, Index, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class PriceHistory(Base):
    __tablename__ = "price_history"

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )

    ticker: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    price: Mapped[Decimal] = mapped_column(
        Numeric(20, 8),
        nullable=False,
    )

    timestamp: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
    )

    __table_args__ = (
        Index(
            "ix_price_ticker_timestamp",
            "ticker",
            timestamp.desc(),
        ),
    )
