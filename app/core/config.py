from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = (
        "postgresql+psycopg://prices_user:dev_password_123@127.0.0.1:5432/prices"
    )
    redis_url: str = "redis://localhost:6379/0"
    deribit_base_url: str = "https://www.deribit.com/api/v2"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
