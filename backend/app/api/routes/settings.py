"""Settings endpoints (read + validated update of persisted preferences)."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.settings_service import (
    EDITABLE_DEFAULTS,
    SettingsService,
    SettingValidationError,
    validate_settings,
)

router = APIRouter(prefix="/settings", tags=["settings"])


class SettingsUpdate(BaseModel):
    gemini_api_key: str | None = None
    gemini_model: str | None = None
    refresh_interval: int | None = None
    cache_duration: int | None = None
    theme: str | None = None
    language: str | None = None
    output_folder: str | None = None
    log_level: str | None = None
    notifications: bool | None = None
    developer_mode: bool | None = None
    experimental: bool | None = None
    auto_backup: bool | None = None
    update_url: str | None = None


@router.get("")
def get_settings() -> dict[str, Any]:
    """Return current settings. Secret values are masked."""
    return SettingsService.all(mask_secrets=True)


@router.put("")
def update_settings(payload: SettingsUpdate) -> dict[str, Any]:
    """Validate and persist one or more editable settings."""
    raw = {
        key: value
        for key, value in payload.model_dump(exclude_unset=True).items()
        if key in EDITABLE_DEFAULTS
    }
    try:
        values = validate_settings(raw)
    except SettingValidationError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    SettingsService.update(values)
    return SettingsService.all(mask_secrets=True)
