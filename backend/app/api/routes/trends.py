"""Trend endpoints (placeholder for Milestone 1).

Returns an empty collection until collectors and the intelligence engine are
implemented in later milestones. The contract is defined now so the frontend
can integrate against a stable shape.
"""

from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/trends", tags=["trends"])


class TrendOut(BaseModel):
    id: int
    title: str
    source: str
    url: str | None = None
    summary: str | None = None
    score: float
    created_at: datetime


class TrendListResponse(BaseModel):
    trends: list[TrendOut]
    generated_at: datetime


@router.get("", response_model=TrendListResponse)
def list_trends() -> TrendListResponse:
    """Return today's ranked trends. Empty until collectors are wired up."""
    return TrendListResponse(trends=[], generated_at=datetime.now(timezone.utc))
