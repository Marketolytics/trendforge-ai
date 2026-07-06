"""Application configuration loaded from environment / .env."""

from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Central application settings.

    Values are read from environment variables prefixed with ``TRENDFORGE_``
    (see ``.env.example``), with sensible local-first defaults.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="TRENDFORGE_",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "TrendForge AI"
    version: str = "0.1.0"

    host: str = "127.0.0.1"
    port: int = 8756

    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173,tauri://localhost"
    database_url: str = "sqlite:///./trendforge.db"

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    """Return a cached Settings instance."""
    return Settings()


settings = get_settings()
