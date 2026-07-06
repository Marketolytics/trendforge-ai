"""Research workspace endpoints (deterministic base + merged AI enrichment)."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query
from sqlmodel import Session, select

from app.db.models import GeneratedContent
from app.db.session import engine
from app.services.research import engine as research_engine

router = APIRouter(prefix="/research", tags=["research"])


def _stored_ai(trend_id: int) -> dict | None:
    with Session(engine) as s:
        row = s.exec(
            select(GeneratedContent)
            .where(GeneratedContent.trend_id == trend_id)
            .where(GeneratedContent.kind == "research")
        ).first()
        if row and row.payload:
            return (row.payload or {}).get("data")
    return None


@router.get("")
def list_research() -> list[dict]:
    return research_engine.list_packages()


@router.get("/{trend_id}")
def get_research(trend_id: int, rebuild: bool = Query(False)) -> dict:
    base = research_engine.get_base(trend_id, rebuild=rebuild)
    if base is None:
        raise HTTPException(status_code=404, detail="Trend not found")
    return {"trend_id": trend_id, "base": base, "ai": _stored_ai(trend_id)}


@router.post("/{trend_id}/build")
def build_research(trend_id: int) -> dict:
    base = research_engine.build_base(trend_id)
    if base is None:
        raise HTTPException(status_code=404, detail="Trend not found")
    return {"trend_id": trend_id, "base": base, "ai": _stored_ai(trend_id)}
