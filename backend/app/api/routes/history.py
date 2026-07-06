"""Refresh/activity history endpoints."""

from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Query
from pydantic import BaseModel, ConfigDict
from sqlmodel import Session, select

from app.db.models import History
from app.db.session import engine

router = APIRouter(prefix="/history", tags=["history"])


class HistoryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    event: str
    status: str
    trends_collected: int
    sources_ok: int
    sources_failed: int
    duration_ms: int
    detail: dict
    created_at: datetime


@router.get("", response_model=list[HistoryOut])
def list_history(limit: int = Query(25, ge=1, le=200)) -> list[HistoryOut]:
    with Session(engine) as session:
        rows = session.exec(
            select(History).order_by(History.created_at.desc()).limit(limit)
        ).all()
        return [HistoryOut.model_validate(r) for r in rows]
