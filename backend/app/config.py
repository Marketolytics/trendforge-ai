"""Application configuration loaded from environment / .env.

Config values here are the *defaults* and infrastructure-level settings
(paths, ports). User-editable preferences (refresh interval, cache duration,
Gemini key, theme, output folder, log level) are persisted in the database
via ``SettingsService`` and seeded from these defaults on first launch.
"""

from __future__ import annotations

import os
import sys
from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# Backend root directory (…/backend), i.e. the parent of the ``app`` package.
BASE_DIR = Path(__file__).resolve().parent.parent


def _is_writable(path: Path) -> bool:
    try:
        path.mkdir(parents=True, exist_ok=True)
        probe = path / ".write_test"
        probe.write_text("ok", encoding="utf-8")
        probe.unlink()
        return True
    except Exception:  # noqa: BLE001
        return False


def _default_data_dir() -> str:
    """Resolve the workspace root, auto-detecting a writable location.

    - explicit ``TRENDFORGE_DATA_DIR`` env wins (used by the desktop launcher),
    - a packaged build stores user data in ``%LOCALAPPDATA%\\TrendForge AI``
      (so upgrades never touch it), falling back to the home directory or a
      portable folder beside the executable if that isn't writable,
    - development uses ``backend/data``.
    """
    env = os.environ.get("TRENDFORGE_DATA_DIR")
    if env:
        return env
    if getattr(sys, "frozen", False):  # PyInstaller / packaged sidecar
        candidates: list[Path] = []
        local = os.environ.get("LOCALAPPDATA")
        if local:
            candidates.append(Path(local) / "TrendForge AI")
        candidates.append(Path.home() / "TrendForge AI")
        candidates.append(Path(sys.executable).resolve().parent / "TrendForge-Data")
        for candidate in candidates:
            if _is_writable(candidate):
                return str(candidate)
        return str(Path.home() / "TrendForge AI")
    return str(BASE_DIR / "data")


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
    version: str = "1.0.0"

    host: str = "127.0.0.1"
    port: int = 8756

    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173,tauri://localhost"

    # --- Filesystem layout ------------------------------------------------
    # The workspace root; all local data lives here.
    data_dir: str = Field(default_factory=_default_data_dir)
    database_path: str = ""  # empty -> <data_dir>/trendforge.db
    log_dir: str = ""        # empty -> <data_dir>/logs
    output_folder: str = ""  # empty -> <data_dir>/exports

    # --- User-editable defaults (persisted to DB on first launch) ---------
    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.5-flash"
    refresh_interval: int = 3600   # seconds between auto refreshes
    cache_duration: int = 1800     # seconds a cached request stays fresh
    theme: str = "dark"
    language: str = "en"
    log_level: str = "INFO"
    notifications: bool = True
    developer_mode: bool = False
    experimental: bool = False
    auto_backup: bool = False
    update_url: str = ""           # optional URL returning {"version": "x.y.z"}

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
    def resolved_projects_dir(self) -> Path:
        return self.data_path / "projects"

    @property
    def resolved_cache_dir(self) -> Path:
        return self.data_path / "cache"

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

    @property
    def database_url(self) -> str:
        return f"sqlite:///{self.resolved_database_path.as_posix()}"

    def ensure_dirs(self) -> None:
        """Create the full workspace directory tree (idempotent)."""
        self.resolved_database_path.parent.mkdir(parents=True, exist_ok=True)
        for path in self.workspace_dirs.values():
            path.mkdir(parents=True, exist_ok=True)


@lru_cache
def get_settings() -> Settings:
    """Return a cached Settings instance."""
    s = Settings()
    s.ensure_dirs()
    return s


settings = get_settings()
