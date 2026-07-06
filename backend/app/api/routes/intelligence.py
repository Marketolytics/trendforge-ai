"""Analytics + projects/history endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Query

from app.services import projects_service
from app.services.intelligence import analytics

router = APIRouter(prefix="/intelligence", tags=["intelligence"])


@router.get("/analytics")
def get_analytics() -> dict:
    return analytics.compute()


@router.get("/projects")
def list_projects(
    q: str | None = Query(None),
    sort: str = Query("recent", pattern="^(recent|modules|title)$"),
) -> list[dict]:
    return projects_service.list_projects(q=q, sort=sort)
