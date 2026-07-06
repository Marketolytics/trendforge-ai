"""AI analysis orchestrator.

For a given trend and analysis *kind* it:
  1. returns the persisted result if one exists (unless ``force``),
  2. otherwise builds context (including real "existing coverage" from the DB),
  3. renders the versioned prompt, calls Gemini, parses into a typed model,
  4. persists the result to ``generated_content`` and returns it.

Persistence in ``generated_content`` is what prevents duplicate Gemini calls
and powers regeneration (``force=True`` overwrites).
"""

from __future__ import annotations

from datetime import datetime, timezone

from pydantic import BaseModel
from sqlalchemy import or_
from sqlmodel import Session, select

from app.core.logging import get_logger
from app.db.models import GeneratedContent, Trend
from app.db.session import engine
from app.schemas.ai import (
    ContentStrategy,
    Hooks,
    Titles,
    TrendAnalysis,
    TrendSummary,
    ThumbnailStrategy,
)
from app.services.ai.gemini_service import gemini_service
from app.services.ai.prompt_manager import prompt_manager
from app.services.ai.response_parser import parse_into

log = get_logger("trendforge.ai.analyzer")

# kind -> (prompt template name, output schema)
GENERATORS: dict[str, tuple[str, type[BaseModel]]] = {
    "analysis": ("trend_analysis", TrendAnalysis),
    "summary": ("summary", TrendSummary),
    "strategy": ("content_strategy", ContentStrategy),
    "hooks": ("hooks", Hooks),
    "titles": ("titles", Titles),
    "thumbnail": ("thumbnail", ThumbnailStrategy),
}


class TrendNotFoundError(Exception):
    pass


def _iso(dt: datetime | None) -> str:
    if dt is None:
        return "unknown"
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.isoformat()


def _related_headlines(session: Session, trend: Trend, limit: int = 8) -> str:
    """Pull sibling headlines sharing a keyword — real 'existing coverage'."""
    if not trend.keywords:
        return "No related coverage found."
    # Match any keyword appearing in another trend's title.
    clauses = [Trend.title.ilike(f"%{kw}%") for kw in trend.keywords[:5]]
    rows = session.exec(
        select(Trend)
        .where(Trend.id != trend.id)
        .where(or_(*clauses))
        .order_by(Trend.score.desc())
        .limit(limit)
    ).all()
    if not rows:
        return "No related coverage found."
    return "\n".join(f"- {r.title} ({r.source})" for r in rows)


def _build_context(session: Session, trend: Trend) -> dict:
    return {
        "title": trend.title,
        "summary": trend.summary or "(no summary provided)",
        "source": trend.source,
        "source_type": trend.source_type,
        "url": trend.url or "",
        "category": trend.category,
        "region": trend.region,
        "published": _iso(trend.published_time),
        "cluster_size": trend.cluster_size,
        "keywords": ", ".join(trend.keywords) or "(none)",
        "existing_coverage": _related_headlines(session, trend),
        "previous_scene": "",
    }


def _load_stored(session: Session, trend_id: int, kind: str) -> GeneratedContent | None:
    return session.exec(
        select(GeneratedContent)
        .where(GeneratedContent.trend_id == trend_id)
        .where(GeneratedContent.kind == kind)
    ).first()


async def generate(trend_id: int, kind: str, *, force: bool = False) -> dict:
    """Generate (or fetch cached) analysis of ``kind`` for a trend."""
    if kind not in GENERATORS:
        raise ValueError(f"unknown analysis kind: {kind}")
    prompt_name, schema = GENERATORS[kind]

    with Session(engine) as session:
        trend = session.get(Trend, trend_id)
        if trend is None:
            raise TrendNotFoundError(f"trend {trend_id} not found")

        if not force:
            stored = _load_stored(session, trend_id, kind)
            if stored is not None:
                payload = stored.payload or {}
                return {
                    "kind": kind,
                    "trend_id": trend_id,
                    "prompt_version": payload.get("version", "unknown"),
                    "cached": True,
                    "generated_at": _iso(stored.created_at),
                    "data": payload.get("data", {}),
                }

        context = _build_context(session, trend)
        trend_title = trend.title

    # Render + call Gemini outside the DB session.
    rendered, template = prompt_manager.render(prompt_name, context)
    raw = await gemini_service.generate_json(
        rendered, temperature=template.temperature, label=kind
    )
    model = parse_into(raw, schema)
    data = model.model_dump()

    now = datetime.now(timezone.utc)
    with Session(engine) as session:
        row = _load_stored(session, trend_id, kind)
        if row is None:
            row = GeneratedContent(trend_id=trend_id, title=trend_title, kind=kind)
        row.payload = {"version": template.version, "data": data}
        row.status = "generated"
        row.created_at = now
        session.add(row)
        session.commit()

    log.info(
        "ai generation stored",
        extra={"category": "ai", "kind": kind, "trend_id": trend_id, "version": template.version},
    )
    return {
        "kind": kind,
        "trend_id": trend_id,
        "prompt_version": template.version,
        "cached": False,
        "generated_at": _iso(now),
        "data": data,
    }


async def get_opportunity(trend_id: int, *, force: bool = False) -> dict:
    """Opportunity score is derived from the comprehensive analysis."""
    result = await generate(trend_id, "analysis", force=force)
    result = dict(result)
    result["kind"] = "opportunity"
    result["data"] = (result.get("data") or {}).get("opportunity", {})
    return result
