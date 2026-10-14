from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class PriceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    ticker: str
    price: Decimal
    timestamp: int
