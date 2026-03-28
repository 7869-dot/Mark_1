"""Application settings (12-factor, Pydantic Settings v2)."""

from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic import AliasChoices, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "persona-ai"
    environment: Literal["development", "staging", "production"] = "development"
    debug: bool = False
    api_v1_prefix: str = "/api/v1"

    host: str = "0.0.0.0"
    port: int = 8000

    database_url: str = Field(
        validation_alias=AliasChoices("DATABASE_URL", "database_url"),
        description="Async SQLAlchemy URL, e.g. postgresql+asyncpg://user:pass@host:5432/db",
    )

    secret_key: str = Field(
        min_length=32,
        validation_alias=AliasChoices("SECRET_KEY", "secret_key"),
    )
    access_token_expire_minutes: int = 60 * 24 * 7
    algorithm: str = "HS256"

    cors_origins: str = Field(
        default="http://localhost:3000",
        validation_alias=AliasChoices("CORS_ORIGINS", "cors_origins"),
    )

    rate_limit_default: str = "120/minute"
    rate_limit_auth: str = "30/minute"

    embedding_api_key: str | None = Field(default=None, validation_alias="EMBEDDING_API_KEY")
    embedding_api_base: str = Field(
        default="https://api.openai.com/v1",
        validation_alias="EMBEDDING_API_BASE",
    )
    embedding_model: str = Field(
        default="text-embedding-3-small",
        validation_alias="EMBEDDING_MODEL",
    )
    embedding_dimensions: int = Field(
        default=1536,
        ge=32,
        le=8192,
        validation_alias="EMBEDDING_DIMENSIONS",
    )
    embedding_fake: bool = Field(default=False, validation_alias="EMBEDDING_FAKE")

    @field_validator("embedding_fake", mode="before")
    @classmethod
    def parse_bool(cls, v: object) -> bool:
        if isinstance(v, bool):
            return v
        if v is None:
            return False
        s = str(v).strip().lower()
        return s in {"1", "true", "yes", "on"}

    @property
    def cors_origin_list(self) -> list[str]:
        raw = self.cors_origins.strip()
        if raw == "*":
            return ["*"]
        return [o.strip() for o in raw.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
