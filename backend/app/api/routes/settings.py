"""Settings endpoints (read + update persisted preferences)."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel

from app.services.settings_service import EDITABLE_DEFAULTS, SettingsService

router = APIRouter(prefix="/settings", tags=["settings"])


class SettingsUpdate(BaseModel):
    gemini_api_key: str | None = None
    gemini_model: str | None = None
    refresh_interval: int | None = None
    cache_duration: int | None = None
    theme: str | None = None
    output_folder: str | None = None
    log_level: str | None = None


@router.get("")
def get_settings() -> dict[str, Any]:
    """Return current settings. Secret values are masked."""
    return SettingsService.all(mask_secrets=True)


@router.put("")
def update_settings(payload: SettingsUpdate) -> dict[str, Any]:
    """Update one or more editable settings."""
    values = {
        key: value
        for key, value in payload.model_dump(exclude_unset=True).items()
        if key in EDITABLE_DEFAULTS
    }
    SettingsService.update(values)
    return SettingsService.all(mask_secrets=True)
