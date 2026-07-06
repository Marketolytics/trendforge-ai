"""OpenAI-compatible provider.

Works with any endpoint exposing the OpenAI Chat Completions API — OpenAI,
OpenRouter, LM Studio and Ollama — differentiated only by base URL and whether
a key is required. This is how future providers plug in without touching the
rest of TrendForge.
"""

from __future__ import annotations

import time

import httpx

from app.services.ai import credentials
from app.services.ai.providers.base import (
    AIProvider,
    ConnectionResult,
    GenerationResult,
    ModelInfo,
    NotConfiguredError,
    ProviderError,
)


class OpenAICompatibleProvider(AIProvider):
    requires_key = True

    def __init__(self, name: str, label: str, base_url: str, requires_key: bool = True,
                 default_models: list[str] | None = None) -> None:
        self.name = name
        self.label = label
        self.base_url = base_url.rstrip("/")
        self.requires_key = requires_key
        self.default_models = default_models or []

    def _key(self) -> str:
        return (credentials.get_key(self.name) or "").strip()

    def is_configured(self) -> bool:
        return (not self.requires_key) or bool(self._key())

    def _headers(self) -> dict:
        headers = {"Content-Type": "application/json"}
        key = self._key()
        if key:
            headers["Authorization"] = f"Bearer {key}"
        return headers

    async def list_models(self) -> list[ModelInfo]:
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(f"{self.base_url}/models", headers=self._headers())
                resp.raise_for_status()
                data = resp.json().get("data", [])
                models = [ModelInfo(id=m["id"], label=m.get("id", "")) for m in data if m.get("id")]
                return models or [ModelInfo(id=m) for m in self.default_models]
        except Exception:  # noqa: BLE001
            return [ModelInfo(id=m) for m in self.default_models]

    async def validate(self) -> ConnectionResult:
        if self.requires_key and not self._key():
            return ConnectionResult(ok=False, error="No API key configured")
        start = time.perf_counter()
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(f"{self.base_url}/models", headers=self._headers())
                resp.raise_for_status()
            latency = round((time.perf_counter() - start) * 1000, 1)
            return ConnectionResult(ok=True, latency_ms=latency, models=await self.list_models())
        except httpx.HTTPStatusError as exc:
            return ConnectionResult(ok=False, error=f"HTTP {exc.response.status_code}")
        except Exception as exc:  # noqa: BLE001
            return ConnectionResult(ok=False, error=str(exc))

    async def generate(
        self, prompt: str, *, model: str, temperature: float = 0.6, max_output_tokens: int = 8192
    ) -> GenerationResult:
        if self.requires_key and not self._key():
            raise NotConfiguredError(f"{self.label} API key is not set.")
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temperature,
            "max_tokens": max_output_tokens,
            "response_format": {"type": "json_object"},
        }
        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                resp = await client.post(
                    f"{self.base_url}/chat/completions", headers=self._headers(), json=payload
                )
                resp.raise_for_status()
                data = resp.json()
        except httpx.HTTPStatusError as exc:
            raise ProviderError(f"{self.label} error: HTTP {exc.response.status_code}") from exc
        except Exception as exc:  # noqa: BLE001
            raise ProviderError(f"{self.label} request failed: {exc}") from exc

        text = (data.get("choices") or [{}])[0].get("message", {}).get("content", "")
        usage = data.get("usage", {}) or {}
        return GenerationResult(
            text=text or "",
            prompt_tokens=usage.get("prompt_tokens", 0) or 0,
            response_tokens=usage.get("completion_tokens", 0) or 0,
            model=model,
        )
