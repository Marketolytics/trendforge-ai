"""Application configuration loaded from environment / .env.

Config values here are the *defaults* and infrastructure-level settings
(paths, ports). User-editable preferences (refresh interval, cache duration,
Gemini key, theme, output folder, log level) are persisted in the database
via ``SettingsService`` and seeded from these defaults on first launch.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# Backend root directory (…/backend), i.e. the parent of the ``app`` package.
BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    """Central application settings.

    Environment variables are prefixed with ``TRENDFORGE_`` (see
    ``.env.example``), with sensible local-first defaults.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="TRENDFORGE_",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "TrendForge AI"
    version: str = "0.2.0"

    host: str = "127.0.0.1"
    port: int = 8756

    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173,tauri://localhost"

    # --- Filesystem layout ------------------------------------------------
    # All local data lives under a single data directory by default.
    data_dir: str = str(BASE_DIR / "data")
    database_path: str = ""  # empty -> <data_dir>/trendforge.db
    log_dir: str = ""        # empty -> <data_dir>/logs
    output_folder: str = ""  # empty -> <data_dir>/exports

    # --- User-editable defaults (persisted to DB on first launch) ---------
    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.5-flash"
    refresh_interval: int = 3600   # seconds between auto refreshes
    cache_duration: int = 1800     # seconds a cached request stays fresh
    theme: str = "dark"
    log_level: str = "INFO"

    # ---------------------------------------------------------------------
    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def data_path(self) -> Path:
        return Path(self.data_dir)

    @property
    def resolved_database_path(self) -> Path:
        return Path(self.database_path) if self.database_path else self.data_path / "trendforge.db"

    @property
    def resolved_log_dir(self) -> Path:
        return Path(self.log_dir) if self.log_dir else self.data_path / "logs"

    @property
    def resolved_output_folder(self) -> Path:
        return Path(self.output_folder) if self.output_folder else self.data_path / "exports"

    @property
    def database_url(self) -> str:
        return f"sqlite:///{self.resolved_database_path.as_posix()}"

    def ensure_dirs(self) -> None:
        """Create the local data directories if they don't exist."""
        self.data_path.mkdir(parents=True, exist_ok=True)
        self.resolved_database_path.parent.mkdir(parents=True, exist_ok=True)
        self.resolved_log_dir.mkdir(parents=True, exist_ok=True)
        self.resolved_output_folder.mkdir(parents=True, exist_ok=True)


@lru_cache
def get_settings() -> Settings:
    """Return a cached Settings instance."""
    s = Settings()
    s.ensure_dirs()
    return s


settings = get_settings()
