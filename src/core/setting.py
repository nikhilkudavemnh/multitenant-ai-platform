import os
from datetime import timedelta

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    POSTGRES_USER: str = os.environ.get("POSTGRES_USER", "")
    POSTGRES_PASSWORD: str = os.environ.get("POSTGRES_PASSWORD", "")
    POSTGRES_HOST: str = os.environ.get("POSTGRES_HOST", "localhost")
    POSTGRES_DB: str = os.environ.get("POSTGRES_DB", "")
    POSTGRES_PORT: int = 5432

    ADMIN_EMAIL: str = os.environ.get("ADMIN_EMAIL", "admin@example.com")
    ADMIN_PASSWORD_HASH: str = os.environ.get("ADMIN_PASSWORD_HASH", "-")

    SECRET_KEY: str = os.environ.get("SECRET_KEY", "change-me-in-production")
    ALGORITHM: str = "HS256"
    JWT_EXPIRATION_DELTA: timedelta = timedelta(minutes=15)
    JWT_REFRESH_EXPIRATION_DELTA: timedelta = timedelta(days=7)

    EXCLUDE_URL: frozenset[str] = frozenset({
        "/docs",
        "/openapi.json"
    })


settings = Settings()