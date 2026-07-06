"""Aggregate all API routers under a single prefix."""

from __future__ import annotations

from fastapi import APIRouter

from app.api.routes import (
    ai,
    cache,
    content,
    health,
    history,
    settings,
    sources,
    trends,
)

api_router = APIRouter(prefix="/api")
api_router.include_router(health.router)
api_router.include_router(trends.router)
api_router.include_router(sources.router)
api_router.include_router(history.router)
api_router.include_router(settings.router)
api_router.include_router(cache.router)
api_router.include_router(ai.router)
api_router.include_router(content.router)
