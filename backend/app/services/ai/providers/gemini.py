"""Google Gemini provider."""

from __future__ import annotations

import re
import time
from collections.abc import AsyncIterator

from google import genai
from google.genai import errors, types

from app.services.ai import credentials
from app.services.ai.providers.base import (
    AIProvider,
    ConnectionResult,
    GenerationResult,
    ModelInfo,
    NotConfiguredError,
    ProviderError,
)


class GeminiProvider(AIProvider):
    name = "gemini"
    label = "Google Gemini"
    requires_key = True
    default_models = ["gemini-2.5-flash", "gemini-2.5-pro", "gemini-2.0-flash"]

    def __init__(self) -> None:
        self._client: genai.Client | None = None
        self._client_key: str | None = None

    def _key(self) -> str:
        return (credentials.get_key(self.name) or "").strip()

    def is_configured(self) -> bool:
        return bool(self._key())

    def _get_client(self) -> genai.Client:
        key = self._key()
        if not key:
            raise NotConfiguredError("Gemini API key is not set.")
        if self._client is None or self._client_key != key:
            self._client = genai.Client(api_key=key)
            self._client_key = key
        return self._client

    async def _fetch_models(self) -> list[ModelInfo]:
        """Real API call — raises on auth/network errors (no fallback)."""
        client = self._get_client()
        models = await client.aio.models.list()
        out: list[ModelInfo] = []
        for m in models:
            actions = getattr(m, "supported_actions", None) or getattr(m, "supported_generation_methods", [])
            if not actions or "generateContent" in actions:
                mid = (m.name or "").replace("models/", "")
                if mid:
                    out.append(ModelInfo(id=mid, label=getattr(m, "display_name", "") or mid))
        return out

    async def list_models(self) -> list[ModelInfo]:
        try:
            return await self._fetch_models() or [ModelInfo(id=m) for m in self.default_models]
        except Exception:  # noqa: BLE001 - generation-time robustness
            return [ModelInfo(id=m) for m in self.default_models]

    async def validate(self) -> ConnectionResult:
        if not self.is_configured():
            return ConnectionResult(ok=False, error="No API key configured")
        start = time.perf_counter()
        try:
            models = await self._fetch_models()  # surfaces bad-key errors
            latency = round((time.perf_counter() - start) * 1000, 1)
            return ConnectionResult(ok=True, latency_ms=latency, models=models or [ModelInfo(id=m) for m in self.default_models])
        except errors.APIError as exc:
            return ConnectionResult(ok=False, error=f"Gemini error ({getattr(exc, 'code', '?')}): {exc}")
        except Exception as exc:  # noqa: BLE001
            return ConnectionResult(ok=False, error=str(exc))

    async def generate(
        self, prompt: str, *, model: str, temperature: float = 0.6, max_output_tokens: int = 8192
    ) -> GenerationResult:
        client = self._get_client()
        config = types.GenerateContentConfig(
            temperature=temperature,
            max_output_tokens=max_output_tokens,
            response_mime_type="application/json",
        )
        try:
            resp = await client.aio.models.generate_content(model=model, contents=prompt, config=config)
        except errors.APIError as exc:
            raise _friendly_error(exc) from exc
        text = resp.text or ""
        usage = getattr(resp, "usage_metadata", None)
        return GenerationResult(
            text=text,
            prompt_tokens=getattr(usage, "prompt_token_count", 0) or 0,
            response_tokens=getattr(usage, "candidates_token_count", 0) or 0,
            model=model,
        )

    async def stream(
        self, prompt: str, *, model: str, temperature: float = 0.6, max_output_tokens: int = 8192
    ) -> AsyncIterator[str]:
        client = self._get_client()
        config = types.GenerateContentConfig(temperature=temperature, max_output_tokens=max_output_tokens)
        stream = await client.aio.models.generate_content_stream(model=model, contents=prompt, config=config)
        async for chunk in stream:
            if chunk.text:
                yield chunk.text


def _friendly_error(exc: errors.APIError) -> ProviderError:
    """Turn a raw Gemini APIError into a concise, user-facing ProviderError."""
    code = getattr(exc, "code", None)
    raw = str(exc)

    if code == 429:
        m = re.search(r"retry in (\d+(?:\.\d+)?)s", raw)
        retry_after = float(m.group(1)) if m else None
        return ProviderError(
            "Gemini rate limit reached. The free tier allows only a few requests per "
            "minute — wait a moment and try again, or upgrade your plan / switch model "
            "in Settings → AI Provider.",
            code=429,
            retry_after=retry_after,
        )
    if code in (400, 401, 403):
        return ProviderError(
            "Gemini rejected the request. Check your API key and selected model in "
            "Settings → AI Provider.",
            code=code,
        )
    if code in (500, 502, 503, 504):
        return ProviderError(
            "Gemini is temporarily unavailable. Please try again in a moment.", code=code
        )
    # Fallback: keep the first line only so we never surface a giant JSON blob.
    short = raw.split("\n", 1)[0][:200]
    return ProviderError(f"Gemini error ({code}): {short}", code=code)
