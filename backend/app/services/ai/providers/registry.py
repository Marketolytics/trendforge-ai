"""Provider registry. Add a new provider here and the whole app can use it."""

from __future__ import annotations

from app.services.ai.providers.base import AIProvider
from app.services.ai.providers.gemini import GeminiProvider
from app.services.ai.providers.openai_compatible import OpenAICompatibleProvider

PROVIDERS: dict[str, AIProvider] = {
    "gemini": GeminiProvider(),
    "openai": OpenAICompatibleProvider(
        "openai", "OpenAI", "https://api.openai.com/v1", requires_key=True,
        default_models=["gpt-4o", "gpt-4o-mini", "o3-mini"],
    ),
    "openrouter": OpenAICompatibleProvider(
        "openrouter", "OpenRouter", "https://openrouter.ai/api/v1", requires_key=True,
        default_models=["openai/gpt-4o", "anthropic/claude-3.5-sonnet", "google/gemini-2.5-flash"],
    ),
    "ollama": OpenAICompatibleProvider(
        "ollama", "Ollama (local)", "http://localhost:11434/v1", requires_key=False,
        default_models=["llama3.1", "qwen2.5", "mistral"],
    ),
    "lmstudio": OpenAICompatibleProvider(
        "lmstudio", "LM Studio (local)", "http://localhost:1234/v1", requires_key=False,
        default_models=["local-model"],
    ),
}

DEFAULT_PROVIDER = "gemini"


def get_provider(name: str | None = None) -> AIProvider:
    return PROVIDERS.get(name or "", PROVIDERS[DEFAULT_PROVIDER])


def provider_meta() -> list[dict]:
    return [
        {
            "name": p.name,
            "label": p.label,
            "requires_key": p.requires_key,
            "base_url": p.base_url,
            "default_models": p.default_models,
        }
        for p in PROVIDERS.values()
    ]
