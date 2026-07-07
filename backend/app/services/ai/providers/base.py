"""Provider interface + shared result types.

Every provider implements the same surface so the rest of TrendForge stays
vendor-agnostic:

    validate()      -> ConnectionResult   (key/endpoint check + latency)
    list_models()   -> list[ModelInfo]
    generate()      -> GenerationResult    (text + token usage)
    stream()        -> async iterator of text chunks
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import AsyncIterator
from dataclasses import dataclass, field


@dataclass
class ModelInfo:
    id: str
    label: str = ""


@dataclass
class ConnectionResult:
    ok: bool
    latency_ms: float = 0.0
    models: list[ModelInfo] = field(default_factory=list)
    error: str | None = None


@dataclass
class GenerationResult:
    text: str
    prompt_tokens: int = 0
    response_tokens: int = 0
    model: str = ""


class ProviderError(Exception):
    """Raised for provider-level failures (network, auth, bad response).

    ``code`` carries the provider/HTTP status when known, and ``retry_after``
    the server-suggested delay (seconds) for rate-limit errors so the caller
    can back off intelligently.
    """

    def __init__(
        self,
        message: str,
        *,
        code: int | str | None = None,
        retry_after: float | None = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.retry_after = retry_after


class NotConfiguredError(ProviderError):
    """Raised when the provider is missing a required key/endpoint."""


class AIProvider(ABC):
    """Common interface for all AI providers."""

    #: machine name, e.g. "gemini"
    name: str = "base"
    #: human label
    label: str = "Base"
    #: whether an API key is required (local providers may not need one)
    requires_key: bool = True
    #: default base URL (for OpenAI-compatible providers)
    base_url: str = ""
    #: sensible default models to offer if list_models is unavailable
    default_models: list[str] = []

    @abstractmethod
    def is_configured(self) -> bool:
        """Whether the provider has everything it needs to run."""

    @abstractmethod
    async def validate(self) -> ConnectionResult:
        """Check connectivity/credentials and (if possible) list models."""

    @abstractmethod
    async def list_models(self) -> list[ModelInfo]:
        """Return available models."""

    @abstractmethod
    async def generate(
        self, prompt: str, *, model: str, temperature: float = 0.6, max_output_tokens: int = 8192
    ) -> GenerationResult:
        """Generate a (JSON) completion."""

    async def stream(
        self, prompt: str, *, model: str, temperature: float = 0.6, max_output_tokens: int = 8192
    ) -> AsyncIterator[str]:
        """Stream a completion. Default: yield the full result once."""
        result = await self.generate(
            prompt, model=model, temperature=temperature, max_output_tokens=max_output_tokens
        )
        yield result.text
