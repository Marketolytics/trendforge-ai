"""Settings persistence + validation."""

from __future__ import annotations

import pytest

from app.services.settings_service import (
    SettingsService,
    SettingValidationError,
    validate_settings,
)


def test_set_and_get():
    SettingsService.set("gemini_model", "gemini-test")
    assert SettingsService.get("gemini_model") == "gemini-test"


def test_validate_accepts_valid():
    clean = validate_settings({"refresh_interval": 120, "theme": "dark", "notifications": True})
    assert clean["refresh_interval"] == 120
    assert clean["theme"] == "dark"
    assert clean["notifications"] is True


def test_validate_rejects_bad_interval():
    with pytest.raises(SettingValidationError):
        validate_settings({"refresh_interval": 5})


def test_validate_rejects_bad_theme():
    with pytest.raises(SettingValidationError):
        validate_settings({"theme": "rainbow"})


def test_secrets_masked():
    SettingsService.set("gemini_api_key", "secret123")
    data = SettingsService.all(mask_secrets=True)
    assert data["gemini_api_key"] != "secret123"
    assert data["gemini_api_key_set"] is True
