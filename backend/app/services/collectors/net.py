"""Shared, cached network helpers for collectors.

All outbound HTTP goes through here so every request is consistently
timed out, identified by a User-Agent, and transparently cached.
"""

from __future__ import annotations

from typing import Any

import httpx

from app.core.logging import get_logger
from app.services.cache import cached_fetch, make_key

log = get_logger("trendforge.network")

USER_AGENT = (
    "TrendForgeAI/0.2 (+local desktop content intelligence; contact: local)"
)
DEFAULT_TIMEOUT = httpx.Timeout(15.0, connect=10.0)


async def fetch_text(
    url: str,
    *,
    ttl_seconds: int | None = None,
    force: bool = False,
    headers: dict[str, str] | None = None,
) -> str:
    """GET a URL and return response text, cached by URL."""

    async def _do() -> str:
        async with httpx.AsyncClient(
            timeout=DEFAULT_TIMEOUT,
            follow_redirects=True,
            headers={"User-Agent": USER_AGENT, **(headers or {})},
        ) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            return resp.text

    return await cached_fetch(
        make_key("http_text", url),
        _do,
        ttl_seconds=ttl_seconds,
        namespace="http",
        force=force,
    )


async def fetch_json(
    url: str,
    *,
    ttl_seconds: int | None = None,
    force: bool = False,
    headers: dict[str, str] | None = None,
    params: dict[str, Any] | None = None,
) -> Any:
    """GET a URL and return parsed JSON, cached by URL + params."""

    async def _do() -> Any:
        async with httpx.AsyncClient(
            timeout=DEFAULT_TIMEOUT,
            follow_redirects=True,
            headers={"User-Agent": USER_AGENT, "Accept": "application/json", **(headers or {})},
        ) as client:
            resp = await client.get(url, params=params)
            resp.raise_for_status()
            return resp.json()

    return await cached_fetch(
        make_key("http_json", url, params),
        _do,
        ttl_seconds=ttl_seconds,
        namespace="http",
        force=force,
    )
