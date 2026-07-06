"""AI analysis + content generation orchestrator.

Generic engine shared by every generator (Sprint 3 analysis and Sprint 4
content-factory modules). For a given trend, kind and params it:
  1. returns the persisted result if present (unless ``force``),
  2. builds context — including dependencies (script -> storyboard -> prompts),
  3. renders the versioned prompt, calls Gemini, parses into a typed model,
  4. persists to ``generated_content`` and logs generation time to history.

A "content package" is the set of rows sharing (trend_id, variant), where
``variant`` is the format key (e.g. "60s"). Sprint 3 kinds use an empty variant.
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Callable

from pydantic import BaseModel
from sqlalchemy import or_
from sqlmodel import Session, select

from app.core.logging import get_logger, log_ai
from app.db.models import GeneratedContent, History, Trend
from app.db.session import engine
from app.schemas.ai import (
    BRoll,
    ContentStrategy,
    ContinuityBible,
    Hooks,
    ImagePrompts,
    ProductionChecklist,
    Script,
    SEOPackage,
    Storyboard,
    ThumbnailBlueprint,
    ThumbnailStrategy,
    Titles,
    TrendAnalysis,
    TrendSummary,
    VideoPrompts,
    VoiceOver,
)
from app.services.ai.formats import DEFAULT_FORMAT, get_format
from app.services.ai.gemini_service import gemini_service
from app.services.ai.prompt_manager import prompt_manager
from app.services.ai.response_parser import parse_into

log = get_logger("trendforge.ai.analyzer")

Builder = Callable[[Session, Trend, dict, str, dict], dict]


class TrendNotFoundError(Exception):
    pass


# --- helpers --------------------------------------------------------------

def _iso(dt: datetime | None) -> str:
    if dt is None:
        return "unknown"
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.isoformat()


def _json(obj) -> str:
    return json.dumps(obj, ensure_ascii=False, default=str)


def _related_headlines(session: Session, trend: Trend, limit: int = 8) -> str:
    if not trend.keywords:
        return "No related coverage found."
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


def _base_context(trend: Trend) -> dict:
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
    }


def _load_data(session: Session, trend_id: int, kind: str, variant: str) -> dict | None:
    row = session.exec(
        select(GeneratedContent)
        .where(GeneratedContent.trend_id == trend_id)
        .where(GeneratedContent.kind == kind)
        .where(GeneratedContent.variant == variant)
    ).first()
    if row is None or not row.payload:
        return None
    return (row.payload or {}).get("data")


def _dep(session: Session, trend_id: int, kind: str, variant: str, label: str) -> str:
    data = _load_data(session, trend_id, kind, variant)
    return _json(data) if data else f"({label} not generated yet)"


# --- context builders -----------------------------------------------------

def _b_default(session: Session, trend: Trend, params: dict, variant: str, base: dict) -> dict:
    base["existing_coverage"] = _related_headlines(session, trend)
    return base


def _with_format(params: dict, base: dict) -> dict:
    fmt = get_format(params.get("format", DEFAULT_FORMAT))
    base.update(format_label=fmt.label, seconds=fmt.seconds, scene_hint=fmt.scene_hint)
    return base


def _b_script(session, trend, params, variant, base):
    return _with_format(params, base)


def _b_storyboard(session, trend, params, variant, base):
    base = _with_format(params, base)
    base["script"] = _dep(session, trend.id, "script", variant, "script")
    return base


def _b_continuity(session, trend, params, variant, base):
    base = _with_format(params, base)
    base["script"] = _dep(session, trend.id, "script", variant, "script")
    return base


def _b_scene_prompts(session, trend, params, variant, base):
    base = _with_format(params, base)
    base["storyboard"] = _dep(session, trend.id, "storyboard", variant, "storyboard")
    base["continuity"] = _dep(session, trend.id, "continuity", variant, "continuity bible")
    return base


def _b_voiceover(session, trend, params, variant, base):
    base = _with_format(params, base)
    base["script"] = _dep(session, trend.id, "script", variant, "script")
    base["voice_style"] = params.get("voice_style", "Professional")
    return base


def _b_broll(session, trend, params, variant, base):
    base = _with_format(params, base)
    base["storyboard"] = _dep(session, trend.id, "storyboard", variant, "storyboard")
    return base


def _b_checklist(session, trend, params, variant, base):
    base = _with_format(params, base)
    base["script"] = _dep(session, trend.id, "script", variant, "script")
    return base


def _b_trend_only(session, trend, params, variant, base):
    return base


# --- generator registry ---------------------------------------------------

@dataclass(frozen=True)
class GenSpec:
    prompt: str
    schema: type[BaseModel]
    builder: Builder
    uses_variant: bool = False


GENERATORS: dict[str, GenSpec] = {
    # Sprint 3
    "analysis": GenSpec("trend_analysis", TrendAnalysis, _b_default),
    "summary": GenSpec("summary", TrendSummary, _b_default),
    "strategy": GenSpec("content_strategy", ContentStrategy, _b_default),
    "hooks": GenSpec("hooks", Hooks, _b_default),
    "titles": GenSpec("titles", Titles, _b_default),
    "thumbnail": GenSpec("thumbnail", ThumbnailStrategy, _b_default),
    # Sprint 4 — content factory (format-scoped)
    "script": GenSpec("script", Script, _b_script, uses_variant=True),
    "storyboard": GenSpec("storyboard", Storyboard, _b_storyboard, uses_variant=True),
    "continuity": GenSpec("continuity", ContinuityBible, _b_continuity, uses_variant=True),
    "image_prompts": GenSpec("nano_banana", ImagePrompts, _b_scene_prompts, uses_variant=True),
    "video_prompts": GenSpec("video_prompt", VideoPrompts, _b_scene_prompts, uses_variant=True),
    "voiceover": GenSpec("voiceover", VoiceOver, _b_voiceover, uses_variant=True),
    "broll": GenSpec("broll", BRoll, _b_broll, uses_variant=True),
    "thumbnail_blueprint": GenSpec("thumbnail_blueprint", ThumbnailBlueprint, _b_trend_only, uses_variant=True),
    "seo_package": GenSpec("seo_package", SEOPackage, _b_trend_only, uses_variant=True),
    "checklist": GenSpec("production_checklist", ProductionChecklist, _b_checklist, uses_variant=True),
}

# Ordered module list for a full content package (dependency order).
PACKAGE_KINDS = [
    "script",
    "storyboard",
    "continuity",
    "image_prompts",
    "video_prompts",
    "voiceover",
    "broll",
    "thumbnail_blueprint",
    "seo_package",
    "checklist",
]


def _variant_for(spec: GenSpec, params: dict) -> str:
    return get_format(params.get("format", DEFAULT_FORMAT)).key if spec.uses_variant else ""


def _load_stored(session: Session, trend_id: int, kind: str, variant: str) -> GeneratedContent | None:
    return session.exec(
        select(GeneratedContent)
        .where(GeneratedContent.trend_id == trend_id)
        .where(GeneratedContent.kind == kind)
        .where(GeneratedContent.variant == variant)
    ).first()


def _envelope(kind: str, trend_id: int, variant: str, row_payload: dict, stored: GeneratedContent,
              cached: bool) -> dict:
    return {
        "kind": kind,
        "trend_id": trend_id,
        "variant": variant,
        "prompt_version": row_payload.get("version", stored.prompt_version or "unknown"),
        "cached": cached,
        "generated_at": _iso(stored.created_at),
        "generation_ms": stored.generation_ms,
        "data": row_payload.get("data", {}),
    }


async def generate(trend_id: int, kind: str, *, params: dict | None = None, force: bool = False) -> dict:
    """Generate (or fetch cached) output of ``kind`` for a trend."""
    if kind not in GENERATORS:
        raise ValueError(f"unknown generation kind: {kind}")
    params = params or {}
    spec = GENERATORS[kind]
    variant = _variant_for(spec, params)

    with Session(engine) as session:
        trend = session.get(Trend, trend_id)
        if trend is None:
            raise TrendNotFoundError(f"trend {trend_id} not found")

        if not force:
            stored = _load_stored(session, trend_id, kind, variant)
            if stored is not None and stored.payload:
                return _envelope(kind, trend_id, variant, stored.payload, stored, cached=True)

        context = spec.builder(session, trend, params, variant, _base_context(trend))
        trend_title = trend.title

    rendered, template = prompt_manager.render(spec.prompt, context)

    start = time.perf_counter()
    raw = await gemini_service.generate_json(rendered, temperature=template.temperature, label=kind)
    model = parse_into(raw, spec.schema)
    generation_ms = int((time.perf_counter() - start) * 1000)
    data = model.model_dump()

    now = datetime.now(timezone.utc)
    payload = {"version": template.version, "data": data}
    with Session(engine) as session:
        row = _load_stored(session, trend_id, kind, variant)
        if row is None:
            row = GeneratedContent(trend_id=trend_id, title=trend_title, kind=kind, variant=variant)
        row.payload = payload
        row.params = params
        row.prompt_version = template.version
        row.generation_ms = generation_ms
        row.status = "generated"
        row.created_at = now
        session.add(row)
        session.add(
            History(
                event="ai_generate",
                status="success",
                duration_ms=generation_ms,
                detail={"kind": kind, "variant": variant, "version": template.version},
            )
        )
        session.commit()
        session.refresh(row)
        envelope = _envelope(kind, trend_id, variant, payload, row, cached=False)

    log_ai("generation stored", kind=kind, trend_id=trend_id, variant=variant, duration_ms=generation_ms)
    return envelope


async def get_opportunity(trend_id: int, *, force: bool = False) -> dict:
    """Opportunity score is derived from the comprehensive analysis."""
    result = dict(await generate(trend_id, "analysis", force=force))
    result["kind"] = "opportunity"
    result["data"] = (result.get("data") or {}).get("opportunity", {})
    return result
