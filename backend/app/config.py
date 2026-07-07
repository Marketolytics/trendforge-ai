"""Application configuration loaded from environment / .env.

Config values here are the *defaults* and infrastructure-level settings
(paths, ports). User-editable preferences (refresh interval, cache duration,
Gemini key, theme, output folder, log level) are persisted in the database
via ``SettingsService`` and seeded from these defaults on first launch.
"""

from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# Backend root directory (…/backend), i.e. the parent of the ``app`` package.
BASE_DIR = Path(__file__).resolve().parent.parent


def _running_serverless() -> bool:
    """True on Vercel or any host declaring a serverless/read-only filesystem."""
    return bool(os.environ.get("VERCEL") or os.environ.get("SERVERLESS"))


def _default_data_dir() -> str:
    """Workspace root. On serverless the only writable path is /tmp."""
    if _running_serverless():
        return "/tmp/trendforge"
    return str(BASE_DIR / "data")


class Settings(BaseSettings):
    """Central application settings.

    Values are read from environment variables / a ``.env`` file. Standard,
    deployment-friendly names (``APP_ENV``, ``DATABASE_URL``, ``GEMINI_API_KEY``,
    ``SECRET_KEY``, ``LOG_LEVEL``, ``CACHE_DIRECTORY``, ``EXPORT_DIRECTORY``,
    ``ALLOWED_ORIGINS``) are supported directly; the legacy ``TRENDFORGE_``
    prefixed names still work for backwards compatibility.

    User-editable preferences (refresh interval, cache duration, theme, etc.)
    are persisted in the database via ``SettingsService`` and seeded from these
    defaults on first launch.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="TRENDFORGE_",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = "TrendForge AI"
    version: str = "1.0.0"

    # development | production — controls docs exposure, logging, error detail.
    app_env: str = Field(
        default="development",
        validation_alias=AliasChoices("APP_ENV", "TRENDFORGE_APP_ENV"),
    )
    # Secret used to sign tokens/sessions (reserved for future auth). Generate a
    # random value per deployment; never commit it.
    secret_key: str = Field(
        default="",
        validation_alias=AliasChoices("SECRET_KEY", "TRENDFORGE_SECRET_KEY"),
    )

    host: str = "127.0.0.1"
    port: int = 8000

    # Comma-separated allowed CORS origins (accepts ALLOWED_ORIGINS).
    cors_origins: str = Field(
        default="http://localhost:5173,http://127.0.0.1:5173",
        validation_alias=AliasChoices("ALLOWED_ORIGINS", "TRENDFORGE_CORS_ORIGINS"),
    )

    # --- Database ---------------------------------------------------------
    # Full SQLAlchemy URL. Empty -> local SQLite under the workspace.
    # Production (MySQL) example:
    #   mysql+pymysql://user:password@host:3306/dbname?charset=utf8mb4
    database_url_override: str = Field(
        default="",
        validation_alias=AliasChoices("DATABASE_URL", "TRENDFORGE_DATABASE_URL"),
    )

    # --- Filesystem layout ------------------------------------------------
    # The workspace root; all local data lives here.
    data_dir: str = Field(
        default_factory=_default_data_dir,
        validation_alias=AliasChoices("DATA_DIR", "TRENDFORGE_DATA_DIR"),
    )
    database_path: str = ""  # empty -> <data_dir>/trendforge.db (SQLite only)
    log_dir: str = Field(
        default="",
        validation_alias=AliasChoices("LOG_DIRECTORY", "TRENDFORGE_LOG_DIR"),
    )
    output_folder: str = Field(
        default="",
        validation_alias=AliasChoices("EXPORT_DIRECTORY", "TRENDFORGE_OUTPUT_FOLDER"),
    )
    cache_dir_override: str = Field(
        default="",
        validation_alias=AliasChoices("CACHE_DIRECTORY", "TRENDFORGE_CACHE_DIR"),
    )
    # Path to the built frontend (dist/). Empty -> ../frontend/dist.
    frontend_dist: str = Field(
        default="",
        validation_alias=AliasChoices("FRONTEND_DIST", "TRENDFORGE_FRONTEND_DIST"),
    )

    # --- User-editable defaults (persisted to DB on first launch) ---------
    gemini_api_key: str = Field(
        default="",
        validation_alias=AliasChoices("GEMINI_API_KEY", "TRENDFORGE_GEMINI_API_KEY"),
    )
    gemini_model: str = Field(
        default="gemini-2.5-flash",
        validation_alias=AliasChoices("GEMINI_MODEL", "TRENDFORGE_GEMINI_MODEL"),
    )
    refresh_interval: int = 3600   # seconds between auto refreshes
    cache_duration: int = 1800     # seconds a cached request stays fresh
    theme: str = "dark"
    language: str = "en"
    log_level: str = Field(
        default="INFO",
        validation_alias=AliasChoices("LOG_LEVEL", "TRENDFORGE_LOG_LEVEL"),
    )
    notifications: bool = True
    developer_mode: bool = False
    experimental: bool = False
    auto_backup: bool = False
    update_url: str = ""           # optional URL returning {"version": "x.y.z"}

    # ---------------------------------------------------------------------
    @property
    def is_production(self) -> bool:
        return self.app_env.strip().lower() in ("production", "prod") or self.is_serverless

    @property
    def is_serverless(self) -> bool:
        """Running on a serverless host (Vercel) with an ephemeral filesystem."""
        return _running_serverless()

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
    def database_url(self) -> str:
        """Full SQLAlchemy URL.

        Uses ``DATABASE_URL`` (or Vercel's ``POSTGRES_URL``) when set, else a
        local SQLite database. Postgres URLs are normalized to the psycopg
        (psycopg3) driver so managed providers (Vercel Postgres, Neon,
        Supabase) work with their default ``postgres://`` / ``postgresql://``
        connection strings.
        """
        raw = self.database_url_override.strip() or os.environ.get("POSTGRES_URL", "").strip()
        if not raw:
            return f"sqlite:///{self.resolved_database_path.as_posix()}"
        return self._normalize_db_url(raw)

    @staticmethod
    def _normalize_db_url(url: str) -> str:
        for prefix in ("postgresql+psycopg://", "postgresql+psycopg2://"):
            if url.startswith(prefix):
                return url
        if url.startswith("postgresql://"):
            return "postgresql+psycopg://" + url[len("postgresql://") :]
        if url.startswith("postgres://"):
            return "postgresql+psycopg://" + url[len("postgres://") :]
        return url

    @property
    def is_sqlite(self) -> bool:
        return self.database_url.startswith("sqlite")

    @property
    def resolved_frontend_dist(self) -> Path:
        if self.frontend_dist.strip():
            return Path(self.frontend_dist)
        return BASE_DIR.parent / "frontend" / "dist"

    @property
    def resolved_log_dir(self) -> Path:
        return Path(self.log_dir) if self.log_dir else self.data_path / "logs"

    @property
    def resolved_output_folder(self) -> Path:
        return Path(self.output_folder) if self.output_folder else self.data_path / "exports"

    @property
    def resolved_projects_dir(self) -> Path:
        return self.data_path / "projects"

    @property
    def resolved_cache_dir(self) -> Path:
        return Path(self.cache_dir_override) if self.cache_dir_override else self.data_path / "cache"

    @property
    def resolved_backups_dir(self) -> Path:
        return self.data_path / "backups"

    @property
    def resolved_settings_dir(self) -> Path:
        return self.data_path / "settings"

    @property
    def resolved_temp_dir(self) -> Path:
        return self.data_path / "temp"

    @property
    def workspace_dirs(self) -> dict[str, Path]:
        return {
            "workspace": self.data_path,
            "projects": self.resolved_projects_dir,
            "exports": self.resolved_output_folder,
            "cache": self.resolved_cache_dir,
            "logs": self.resolved_log_dir,
            "backups": self.resolved_backups_dir,
            "settings": self.resolved_settings_dir,
            "temp": self.resolved_temp_dir,
        }

    def ensure_dirs(self) -> None:
        """Create the full workspace directory tree (idempotent)."""
        # Only create the DB parent for local SQLite; external DBs (MySQL) have
        # no local file path.
        if self.is_sqlite:
            self.resolved_database_path.parent.mkdir(parents=True, exist_ok=True)
        for path in self.workspace_dirs.values():
            try:
                path.mkdir(parents=True, exist_ok=True)
            except OSError:
                # On restrictive shared hosts a directory may be pre-created and
                # not user-creatable; ignore if it already exists/usable.
                if not path.exists():
                    raise


@lru_cache
def get_settings() -> Settings:
    """Return a cached Settings instance."""
    s = Settings()
    s.ensure_dirs()
    return s


settings = get_settings()
