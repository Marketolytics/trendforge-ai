"""Backward-compatible shim.

The Gemini-specific service was generalized into a provider-agnostic
:mod:`app.services.ai.service`. This module re-exports the facade under the old
names so existing imports keep working.
"""

from __future__ import annotations

from app.services.ai.service import (
    AIGenerationError,
    AINotConfiguredError,
    ai_service,
)

# Legacy name used throughout the codebase.
gemini_service = ai_service

__all__ = ["ai_service", "gemini_service", "AINotConfiguredError", "AIGenerationError"]
