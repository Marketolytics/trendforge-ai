"""Aggregate all API routers under a single prefix."""

from __future__ import annotations

from fastapi import APIRouter

from app.api.routes import (
    ai,
    cache,
    competitors,
    content,
    dev,
    favorites,
    health,
    history,
    intelligence,
    orchestrator,
    research,
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
api_router.include_router(competitors.router)
api_router.include_router(favorites.router)
api_router.include_router(intelligence.router)
api_router.include_router(orchestrator.router)
api_router.include_router(research.router)
api_router.include_router(dev.router)
api_router.include_router(content.router)
