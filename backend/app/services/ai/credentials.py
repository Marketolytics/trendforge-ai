"""Secure API-key storage via the OS credential store.

Keys are stored in the operating system's credential manager (Windows
Credential Locker, macOS Keychain, Secret Service on Linux) — never in SQLite
or plaintext config. If no keyring backend is available the app degrades
gracefully: it reports keys as unset rather than persisting them insecurely.
"""

from __future__ import annotations

import keyring
from keyring.errors import KeyringError

from app.core.logging import get_logger

log = get_logger("trendforge.credentials")

SERVICE = "TrendForgeAI"


def set_key(provider: str, key: str) -> bool:
    try:
        keyring.set_password(SERVICE, provider, key)
        return True
    except KeyringError as exc:  # noqa: BLE001
        log.warning("keyring set failed", extra={"category": "error", "provider": provider, "error": str(exc)})
        return False


def get_key(provider: str) -> str | None:
    try:
        return keyring.get_password(SERVICE, provider)
    except KeyringError as exc:  # noqa: BLE001
        log.warning("keyring get failed", extra={"category": "error", "provider": provider, "error": str(exc)})
        return None


def delete_key(provider: str) -> bool:
    try:
        keyring.delete_password(SERVICE, provider)
        return True
    except KeyringError:
        return False


def has_key(provider: str) -> bool:
    return bool(get_key(provider))


def backend_available() -> bool:
    try:
        return keyring.get_keyring() is not None
    except Exception:  # noqa: BLE001
        return False
