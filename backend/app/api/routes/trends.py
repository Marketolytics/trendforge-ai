"""Trend endpoints: refresh, today's trends and details."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, HTTPException, Query
from sqlmodel import Session, select

from app.db.models import Trend
from app.db.session import engine
from app.schemas.trends import (
    RefreshResponse,
    TrendDetail,
    TrendListResponse,
    TrendOut,
)
from app.services.aggregation import refresh_trends

router = APIRouter(prefix="/trends", tags=["trends"])


@router.post("/refresh", response_model=RefreshResponse)
async def refresh(force: bool = Query(False, description="Bypass cache")) -> RefreshResponse:
    """Collect fresh trends from all enabled sources and store them."""
    result = await refresh_trends(force=force)
    status = "success"
    if result.sources_failed and result.sources_ok:
        status = "partial"
    elif result.sources_failed and not result.sources_ok:
        status = "error"
    return RefreshResponse(status=status, **result.as_dict())


@router.get("", response_model=TrendListResponse)
def list_trends(
    limit: int = Query(50, ge=1, le=200),
    category: str | None = Query(None),
    source: str | None = Query(None),
    window_hours: int = Query(48, ge=1, le=168, description="Recency window"),
) -> TrendListResponse:
    """Return the highest-scoring recent trends."""
    cutoff = datetime.now(UTC) - timedelta(hours=window_hours)
    with Session(engine) as session:
        stmt = select(Trend).where(Trend.collection_timestamp >= cutoff)
        if category:
            stmt = stmt.where(Trend.category == category)
        if source:
            stmt = stmt.where(Trend.source == source)
        stmt = stmt.order_by(Trend.score.desc()).limit(limit)
        rows = session.exec(stmt).all()

    return TrendListResponse(
        trends=[TrendOut.model_validate(r) for r in rows],
        count=len(rows),
        generated_at=datetime.now(UTC),
    )


@router.get("/{trend_id}", response_model=TrendDetail)
def trend_details(trend_id: int) -> TrendDetail:
    """Return full details for a single trend."""
    with Session(engine) as session:
        row = session.get(Trend, trend_id)
        if row is None:
            raise HTTPException(status_code=404, detail="Trend not found")
        return TrendDetail.model_validate(row)
