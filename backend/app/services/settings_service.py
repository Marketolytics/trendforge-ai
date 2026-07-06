"""Persisted application settings.

Infrastructure defaults live in ``app.config``. User-editable preferences are
stored in the ``settings`` table and seeded from those defaults on first
launch. This service is the single read/write point for runtime settings.
"""

from __future__ import annotations

from typing import Any

from sqlmodel import Session, select

from app.config import settings as env_settings
from app.db.models import Setting, utcnow
from app.db.session import engine

# Keys that are user-editable, with their default values (from env/config).
EDITABLE_DEFAULTS: dict[str, str] = {
    "gemini_api_key": env_settings.gemini_api_key,
    "gemini_model": env_settings.gemini_model,
    "refresh_interval": str(env_settings.refresh_interval),
    "cache_duration": str(env_settings.cache_duration),
    "theme": env_settings.theme,
    "language": env_settings.language,
    "output_folder": str(env_settings.resolved_output_folder),
    "log_level": env_settings.log_level,
    "notifications": str(env_settings.notifications).lower(),
    "developer_mode": str(env_settings.developer_mode).lower(),
    "experimental": str(env_settings.experimental).lower(),
    "auto_backup": str(env_settings.auto_backup).lower(),
    "update_url": env_settings.update_url,
}

# Keys whose value should never be returned in plaintext by the API.
SECRET_KEYS = {"gemini_api_key"}

BOOL_KEYS = {"notifications", "developer_mode", "experimental", "auto_backup"}


class SettingValidationError(ValueError):
    """Raised when a setting fails validation."""


_ALLOWED_LOG_LEVELS = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
_ALLOWED_THEMES = {"dark", "light"}


def validate_settings(values: dict) -> dict:
    """Validate + normalize a partial settings update. Raises on bad input."""
    clean: dict = {}
    for key, value in values.items():
        if key not in EDITABLE_DEFAULTS:
            continue
        if key in ("refresh_interval", "cache_duration"):
            try:
                ivalue = int(value)
            except (TypeError, ValueError) as exc:
                raise SettingValidationError(f"{key} must be an integer") from exc
            if ivalue < 30:
                raise SettingValidationError(f"{key} must be at least 30 seconds")
            clean[key] = ivalue
        elif key == "log_level":
            level = str(value).upper()
            if level not in _ALLOWED_LOG_LEVELS:
                raise SettingValidationError(f"log_level must be one of {sorted(_ALLOWED_LOG_LEVELS)}")
            clean[key] = level
        elif key == "theme":
            if str(value) not in _ALLOWED_THEMES:
                raise SettingValidationError("theme must be 'dark' or 'light'")
            clean[key] = str(value)
        elif key in BOOL_KEYS:
            clean[key] = str(value).lower() in ("1", "true", "yes", "on") if not isinstance(value, bool) else value
        else:
            clean[key] = value
    return clean


class SettingsService:
    """Static access layer over the settings table."""

    @staticmethod
    def seed_defaults() -> None:
        """Insert any missing default settings. Idempotent."""
        with Session(engine) as session:
            existing = {s.key for s in session.exec(select(Setting)).all()}
            for key, value in EDITABLE_DEFAULTS.items():
                if key not in existing:
                    session.add(Setting(key=key, value=value))
            session.commit()

    @staticmethod
    def get(key: str, default: str | None = None) -> str | None:
        with Session(engine) as session:
            row = session.get(Setting, key)
            if row is not None:
                return row.value
        return default if default is not None else EDITABLE_DEFAULTS.get(key)

    @staticmethod
    def get_int(key: str, default: int) -> int:
        raw = SettingsService.get(key)
        try:
            return int(raw) if raw is not None and raw != "" else default
        except (TypeError, ValueError):
            return default

    @staticmethod
    def set(key: str, value: Any) -> None:
        with Session(engine) as session:
            row = session.get(Setting, key)
            if row is None:
                row = Setting(key=key)
            row.value = "" if value is None else str(value)
            row.updated_at = utcnow()
            session.add(row)
            session.commit()

    @staticmethod
    def update(values: dict[str, Any]) -> None:
        for key, value in values.items():
            SettingsService.set(key, value)

    @staticmethod
    def all(mask_secrets: bool = True) -> dict[str, Any]:
        """Return all editable settings, merging DB values over defaults."""
        result: dict[str, Any] = dict(EDITABLE_DEFAULTS)
        with Session(engine) as session:
            for row in session.exec(select(Setting)).all():
                result[row.key] = row.value

        if mask_secrets:
            for key in SECRET_KEYS:
                value = result.get(key) or ""
                result[key] = "" if not value else "••••••••"
                result[f"{key}_set"] = bool(value)

        # Coerce known numeric fields for a clean API contract.
        for numeric in ("refresh_interval", "cache_duration"):
            try:
                result[numeric] = int(result[numeric])
            except (TypeError, ValueError):
                pass
        # Coerce boolean fields.
        for key in BOOL_KEYS:
            if key in result:
                result[key] = str(result[key]).lower() in ("1", "true", "yes", "on")
        return result
