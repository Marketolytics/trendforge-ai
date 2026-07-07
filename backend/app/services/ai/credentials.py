"""API-key resolution and storage.

Resolution order for a provider's key:

1. Environment variable ``<PROVIDER>_API_KEY`` (e.g. ``GEMINI_API_KEY``,
   ``OPENAI_API_KEY``) — the recommended approach for production / shared
   hosting where no OS credential store is available.
2. The OS credential store (Windows Credential Locker, macOS Keychain, Secret
   Service on Linux) via ``keyring`` — used for local desktop-style development.

Keys are never stored in the database or plaintext config. On hosts without a
keyring backend the app degrades gracefully: env-provided keys still work, and
attempts to persist a new key report failure rather than storing insecurely.
"""

from __future__ import annotations

import os

from app.config import settings
from app.core.logging import get_logger

log = get_logger("trendforge.credentials")

SERVICE = "TrendForgeAI"

# Lazily import keyring so a missing/unusable backend never breaks startup.
try:  # pragma: no cover - environment dependent
    import keyring
    from keyring.errors import KeyringError
except Exception:  # noqa: BLE001
    keyring = None  # type: ignore[assignment]

    class KeyringError(Exception):  # type: ignore[no-redef]
        """Fallback when keyring is unavailable."""


def _env_key(provider: str) -> str | None:
    """Return a provider key from the environment, if present."""
    # Gemini has a first-class config field (also reads GEMINI_API_KEY).
    if provider == "gemini" and settings.gemini_api_key.strip():
        return settings.gemini_api_key.strip()
    value = os.environ.get(f"{provider.upper()}_API_KEY")
    return value.strip() if value and value.strip() else None


def set_key(provider: str, key: str) -> bool:
    if keyring is None:
        log.warning(
            "no keyring backend; set an environment variable instead",
            extra={"category": "error", "provider": provider},
        )
        return False
    try:
        keyring.set_password(SERVICE, provider, key)
        return True
    except KeyringError as exc:  # noqa: BLE001
        log.warning(
            "keyring set failed", extra={"category": "error", "provider": provider, "error": str(exc)}
        )
        return False


def get_key(provider: str) -> str | None:
    env = _env_key(provider)
    if env:
        return env
    if keyring is None:
        return None
    try:
        return keyring.get_password(SERVICE, provider)
    except KeyringError as exc:  # noqa: BLE001
        log.warning(
            "keyring get failed", extra={"category": "error", "provider": provider, "error": str(exc)}
        )
        return None


def delete_key(provider: str) -> bool:
    if keyring is None:
        return False
    try:
        keyring.delete_password(SERVICE, provider)
        return True
    except KeyringError:
        return False


def has_key(provider: str) -> bool:
    return bool(get_key(provider))


def backend_available() -> bool:
    """Whether a persistent key store is available (env or keyring)."""
    if keyring is None:
        return False
    try:
        return keyring.get_keyring() is not None
    except Exception:  # noqa: BLE001
        return False
