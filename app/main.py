from fastapi import FastAPI

from app.api.routes.prices import router as prices_router

app = FastAPI(
    title="Deribit Price Tracker",
    description="Historical index prices for BTC and ETH from Deribit.",
    version="1.0.0",
)

app.include_router(prices_router)


@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok"}
