"""Gemini client service.

Wraps the google-genai async client with:
  - runtime API-key resolution (set via Settings, no restart needed),
  - JSON-mode generation,
  - bounded retries with exponential backoff on transient errors,
  - structured logging of every request.
"""

from __future__ import annotations

import asyncio
import time

from google import genai
from google.genai import errors, types

from app.core.logging import get_logger, log_ai
from app.services.settings_service import SettingsService

log = get_logger("trendforge.ai.gemini")

MAX_ATTEMPTS = 3
BASE_BACKOFF = 1.5  # seconds
# HTTP status codes worth retrying (rate limit / transient server errors).
RETRYABLE = {429, 500, 502, 503, 504}


class AINotConfiguredError(Exception):
    """Raised when no Gemini API key is configured."""


class AIGenerationError(Exception):
    """Raised when generation fails after all retries."""


class GeminiService:
    """Thin, resilient wrapper around the Gemini API."""

    def __init__(self) -> None:
        self._client: genai.Client | None = None
        self._client_key: str | None = None

    # -- configuration -----------------------------------------------------
    @staticmethod
    def api_key() -> str:
        return (SettingsService.get("gemini_api_key") or "").strip()

    @staticmethod
    def model() -> str:
        return (SettingsService.get("gemini_model") or "gemini-2.5-flash").strip()

    @property
    def is_configured(self) -> bool:
        return bool(self.api_key())

    def _get_client(self) -> genai.Client:
        key = self.api_key()
        if not key:
            raise AINotConfiguredError(
                "Gemini API key is not set. Add it in Settings to enable AI features."
            )
        # Rebuild the client only when the key changes.
        if self._client is None or self._client_key != key:
            self._client = genai.Client(api_key=key)
            self._client_key = key
        return self._client

    # -- generation --------------------------------------------------------
    async def generate_json(
        self,
        prompt: str,
        *,
        temperature: float = 0.6,
        max_output_tokens: int = 8192,
        label: str = "generate",
    ) -> str:
        """Generate a JSON response, retrying transient failures.

        Returns the raw response text (JSON string) for the parser to handle.
        """
        client = self._get_client()
        model = self.model()
        config = types.GenerateContentConfig(
            temperature=temperature,
            max_output_tokens=max_output_tokens,
            response_mime_type="application/json",
        )

        last_error: Exception | None = None
        for attempt in range(1, MAX_ATTEMPTS + 1):
            start = time.perf_counter()
            try:
                resp = await client.aio.models.generate_content(
                    model=model, contents=prompt, config=config
                )
                text = resp.text or ""
                elapsed = round((time.perf_counter() - start) * 1000, 1)
                log_ai(
                    "gemini request ok",
                    label=label,
                    model=model,
                    attempt=attempt,
                    duration_ms=elapsed,
                    chars=len(text),
                )
                if not text.strip():
                    raise AIGenerationError("empty response from model")
                return text
            except errors.APIError as exc:
                last_error = exc
                code = getattr(exc, "code", None)
                elapsed = round((time.perf_counter() - start) * 1000, 1)
                log_ai(
                    "gemini request failed",
                    label=label,
                    model=model,
                    attempt=attempt,
                    duration_ms=elapsed,
                    code=code,
                    error=str(exc),
                )
                # Auth/permission/bad-request errors are not retryable.
                if code not in RETRYABLE:
                    raise AIGenerationError(f"Gemini error ({code}): {exc}") from exc
            except Exception as exc:  # noqa: BLE001 - network/timeouts etc.
                last_error = exc
                log_ai(
                    "gemini request error",
                    label=label,
                    model=model,
                    attempt=attempt,
                    error=str(exc),
                )

            if attempt < MAX_ATTEMPTS:
                await asyncio.sleep(BASE_BACKOFF * attempt)

        raise AIGenerationError(
            f"Gemini generation failed after {MAX_ATTEMPTS} attempts: {last_error}"
        )


gemini_service = GeminiService()
