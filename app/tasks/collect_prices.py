import asyncio
import logging

from app.db.session import SessionLocal
from app.services.price_service import PriceService
from app.tasks.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(
    name="app.tasks.collect_prices.collect_prices",
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 3},
)
def collect_prices() -> list[dict]:
    with SessionLocal() as session:
        service = PriceService(session)
        records = asyncio.run(service.collect_prices())

    logger.info("Saved index prices: %s", records)
    return [
        {
            "ticker": record["ticker"],
            "price": str(record["price"]),
            "timestamp": record["timestamp"],
        }
        for record in records
    ]
