"""Aggregate all API routers under a single prefix."""

from __future__ import annotations

from fastapi import APIRouter

from app.api.routes import content, health, trends

api_router = APIRouter(prefix="/api")
api_router.include_router(health.router)
api_router.include_router(trends.router)
api_router.include_router(content.router)
