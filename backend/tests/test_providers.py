"""AI provider layer: registry, router and secure credentials."""

from __future__ import annotations

from app.services.ai import credentials, router
from app.services.ai.providers.registry import PROVIDERS, get_provider


def test_registry_has_core_providers():
    for name in ("gemini", "openai", "openrouter", "ollama", "lmstudio"):
        assert name in PROVIDERS
    assert get_provider("gemini").name == "gemini"
    # Unknown falls back to default.
    assert get_provider("nope").name == "gemini"


def test_local_providers_do_not_require_key():
    assert PROVIDERS["ollama"].requires_key is False
    assert PROVIDERS["lmstudio"].requires_key is False
    assert PROVIDERS["openai"].requires_key is True


def test_router_categories():
    assert router.category_for("script") == "content"
    assert router.category_for("analysis") == "research"
    assert router.category_for("quality_review") == "quality"
    assert router.category_for("unknown_kind") == "content"


def test_credentials_roundtrip():
    name = "unittest_provider"
    credentials.delete_key(name)
    assert credentials.has_key(name) is False
    if credentials.set_key(name, "secret-xyz"):
        assert credentials.has_key(name) is True
        assert credentials.get_key(name) == "secret-xyz"
        credentials.delete_key(name)
        assert credentials.has_key(name) is False
