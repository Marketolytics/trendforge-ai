"""Cache inspection and manual clearing endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Query

from app.services.cache import cache

router = APIRouter(prefix="/cache", tags=["cache"])


@router.get("/stats")
def cache_stats() -> dict:
    return cache.stats()


@router.post("/clear")
def clear_cache(namespace: str | None = Query(None)) -> dict:
    """Clear cached requests, optionally limited to one namespace."""
    removed = cache.clear(namespace)
    return {"cleared": removed, "namespace": namespace or "all"}


@router.post("/clear-expired")
def clear_expired() -> dict:
    removed = cache.clear_expired()
    return {"cleared": removed}
