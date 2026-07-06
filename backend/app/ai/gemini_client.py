"""Gemini client interface (stub for Milestone 1).

The real implementation (google-genai SDK calls, retries, prompt assembly)
lands in a later milestone. This stub defines the surface other layers depend
on so they stay decoupled from the concrete SDK.
"""

from __future__ import annotations

from app.config import settings


class GeminiClient:
    """Thin wrapper around the Gemini API."""

    def __init__(self, api_key: str | None = None) -> None:
        self._api_key = api_key or getattr(settings, "gemini_api_key", None)

    @property
    def is_configured(self) -> bool:
        return bool(self._api_key)

    async def generate(self, prompt: str) -> str:  # pragma: no cover - stub
        raise NotImplementedError("Gemini generation is implemented in a later milestone.")
