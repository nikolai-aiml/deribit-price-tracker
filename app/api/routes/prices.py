from datetime import UTC, datetime, time
from datetime import date as Date
from typing import Annotated, Literal

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.price import PriceResponse
from app.services.price_service import PriceService

router = APIRouter(prefix="/api/v1/prices", tags=["Prices"])

Ticker = Literal["btc_usd", "eth_usd"]


@router.get("", response_model=list[PriceResponse])
def get_all_prices(
    ticker: Annotated[Ticker, Query()],
    db: Annotated[Session, Depends(get_db)],):
    return PriceService(db).get_all(ticker)


@router.get("/latest", response_model=PriceResponse)
def get_latest_price(
    ticker: Annotated[Ticker, Query()],
    db: Annotated[Session, Depends(get_db)],):
    result = PriceService(db).get_latest(ticker)
    if result is None:
        raise HTTPException(
            status_code=404,
            detail=f"No price history found for {ticker}",
        )
    return result


@router.get("/by-date", response_model=list[PriceResponse])
def get_prices_by_date(
    ticker: Annotated[Ticker, Query()],
    date: Date,
    db: Annotated[Session, Depends(get_db)],
):
    utc_date = datetime.combine(date, time.min, tzinfo=UTC)
    return PriceService(db).get_by_date(ticker, utc_date)
