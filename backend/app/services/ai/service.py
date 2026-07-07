"""Provider-agnostic AI service.

Resolves the active provider + per-task model via the router, calls the
provider through the common interface, records usage and retries transient
failures. The rest of TrendForge depends only on this facade.
"""

from __future__ import annotations

import asyncio

from app.core.logging import get_logger, log_ai
from app.services.ai import router, usage
from app.services.ai.providers.base import NotConfiguredError, ProviderError
from app.services.ai.providers.registry import get_provider

log = get_logger("trendforge.ai.service")

MAX_ATTEMPTS = 3
BASE_BACKOFF = 1.5
# Cap how long we honor a server-suggested rate-limit delay, so a single
# generation never hangs excessively while still recovering from short limits.
MAX_RETRY_WAIT = 20.0


class AINotConfiguredError(Exception):
    """Raised when the active provider has no key/endpoint configured."""


class AIGenerationError(Exception):
    """Raised when generation fails after all retries."""


class AIService:
    """Facade over the active AI provider."""

    @property
    def is_configured(self) -> bool:
        return get_provider(router.current_provider()).is_configured()

    def provider_name(self) -> str:
        return router.current_provider()

    def model(self, category: str = "content") -> str:
        return router.model_for(category)

    async def generate_json(
        self,
        prompt: str,
        *,
        temperature: float = 0.6,
        max_output_tokens: int = 8192,
        label: str = "generate",
    ) -> str:
        provider = get_provider(router.current_provider())
        category = router.category_for(label)
        model = router.model_for(category)

        if not provider.is_configured():
            raise AINotConfiguredError(
                f"{provider.label} is not configured. Add an API key in Settings → AI Provider."
            )

        last_error: Exception | None = None
        for attempt in range(1, MAX_ATTEMPTS + 1):
            try:
                result = await provider.generate(
                    prompt, model=model, temperature=temperature, max_output_tokens=max_output_tokens
                )
                if not (result.text or "").strip():
                    raise ProviderError("empty response from model")
                usage.record(provider.name, result.prompt_tokens, result.response_tokens)
                log_ai(
                    "generation ok",
                    provider=provider.name,
                    model=model,
                    task=category,
                    label=label,
                    attempt=attempt,
                    prompt_tokens=result.prompt_tokens,
                    response_tokens=result.response_tokens,
                )
                return result.text
            except NotConfiguredError as exc:
                raise AINotConfiguredError(str(exc)) from exc
            except ProviderError as exc:
                last_error = exc
                log_ai(
                    "generation failed",
                    provider=provider.name,
                    model=model,
                    label=label,
                    attempt=attempt,
                    error=str(exc),
                )
                if attempt < MAX_ATTEMPTS:
                    # Honor the server's suggested delay for rate limits (capped),
                    # otherwise use exponential backoff.
                    retry_after = getattr(exc, "retry_after", None)
                    delay = min(retry_after, MAX_RETRY_WAIT) if retry_after else BASE_BACKOFF * attempt
                    await asyncio.sleep(delay)

        raise AIGenerationError(str(last_error))


ai_service = AIService()
