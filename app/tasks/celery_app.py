from celery import Celery
from celery.schedules import crontab

from app.core.config import get_settings

settings = get_settings()

celery_app = Celery(
    "deribit_price_tracker",
    broker=settings.redis_url,
    include=["app.tasks.collect_prices"],
)

celery_app.conf.update(
    timezone="UTC",
    enable_utc=True,
    beat_schedule={
        "collect-index-prices-every-minute": {
            "task": "app.tasks.collect_prices.collect_prices",
            "schedule": crontab(minute="*"),
        },
    },
)
