"""Request cache engine.

A durable, TTL-based cache backed by the ``cached_requests`` table. It sits
in front of every outbound request (RSS, Google Trends, Reddit, news and,
later, Gemini) to avoid redundant network calls.

The store is synchronous (SQLite); async callers use ``cached_fetch`` which
offloads DB access to a thread so the event loop is never blocked.
"""

from __future__ import annotations

import asyncio
import hashlib
import json
from collections.abc import Awaitable, Callable
from datetime import UTC, datetime, timedelta
from typing import Any

from sqlalchemy import delete, func, select
from sqlmodel import Session

from app.core.logging import get_logger
from app.db.models import CachedRequest, utcnow
from app.db.session import engine
from app.services.settings_service import SettingsService

log = get_logger("trendforge.cache")


def _as_utc(dt: datetime) -> datetime:
    """Normalize a possibly-naive datetime (from SQLite) to aware UTC."""
    return dt.replace(tzinfo=UTC) if dt.tzinfo is None else dt.astimezone(UTC)


def make_key(namespace: str, *parts: Any) -> str:
    """Build a stable cache key from a namespace and arbitrary parts."""
    raw = "|".join(str(p) for p in parts)
    digest = hashlib.sha256(raw.encode("utf-8")).hexdigest()[:32]
    return f"{namespace}:{digest}"


class CacheEngine:
    """Synchronous TTL cache over SQLite."""

    def get(self, key: str) -> Any | None:
        with Session(engine) as session:
            row = session.get(CachedRequest, key)
            if row is None:
                return None
            if _as_utc(row.expires_at) <= utcnow():
                session.delete(row)
                session.commit()
                return None
            try:
                return json.loads(row.value)
            except json.JSONDecodeError:
                return None

    def set(self, key: str, value: Any, ttl_seconds: int, namespace: str = "http") -> None:
        now = utcnow()
        expires = now + timedelta(seconds=max(ttl_seconds, 1))
        payload = json.dumps(value, default=str, ensure_ascii=False)
        with Session(engine) as session:
            row = session.get(CachedRequest, key)
            if row is None:
                row = CachedRequest(key=key, namespace=namespace)
            row.value = payload
            row.namespace = namespace
            row.created_at = now
            row.expires_at = expires
            session.add(row)
            session.commit()

    def clear(self, namespace: str | None = None) -> int:
        with Session(engine) as session:
            stmt = delete(CachedRequest)
            if namespace:
                stmt = stmt.where(CachedRequest.namespace == namespace)
            result = session.execute(stmt)
            session.commit()
            return result.rowcount or 0

    def clear_expired(self) -> int:
        with Session(engine) as session:
            stmt = delete(CachedRequest).where(CachedRequest.expires_at <= utcnow())
            result = session.execute(stmt)
            session.commit()
            return result.rowcount or 0

    def stats(self) -> dict[str, Any]:
        now = utcnow()
        with Session(engine) as session:
            total = session.scalar(select(func.count()).select_from(CachedRequest)) or 0
            fresh = (
                session.scalar(
                    select(func.count()).select_from(CachedRequest).where(
                        CachedRequest.expires_at > now
                    )
                )
                or 0
            )
        return {"total": int(total), "fresh": int(fresh), "expired": int(total) - int(fresh)}


cache = CacheEngine()


async def cached_fetch(
    key: str,
    fetch: Callable[[], Awaitable[Any]],
    *,
    ttl_seconds: int | None = None,
    namespace: str = "http",
    force: bool = False,
) -> Any:
    """Return a cached value or fetch, store and return a fresh one.

    ``fetch`` is an async callable performing the actual network request.
    """
    if ttl_seconds is None:
        ttl_seconds = SettingsService.get_int("cache_duration", 1800)

    if not force:
        cached = await asyncio.to_thread(cache.get, key)
        if cached is not None:
            log.debug("cache hit", extra={"category": "cache", "key": key})
            return cached

    value = await fetch()
    await asyncio.to_thread(cache.set, key, value, ttl_seconds, namespace)
    return value
