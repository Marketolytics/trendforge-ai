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
from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime

from pydantic import BaseModel
from sqlalchemy import or_
from sqlmodel import Session, select

from app.core.logging import get_logger, log_ai
from app.db.models import (
    CompetitorVideo,
    GeneratedContent,
    GenerationLog,
    History,
    Trend,
)
from app.db.session import engine
from app.schemas.ai import (
    BRoll,
    CompetitorGap,
    ContentStrategy,
    ContinuityBible,
    Hooks,
    ImagePrompts,
    MultiIdeas,
    ProductionChecklist,
    QualityReview,
    ResearchAI,
    Script,
    SEOPackage,
    Storyboard,
    ThumbnailBlueprint,
    ThumbnailStrategy,
    Titles,
    TrendAnalysis,
    TrendForecast,
    TrendSummary,
    UploadAdvice,
    VideoPrompts,
    VoiceOver,
)
from app.services.ai.formats import DEFAULT_FORMAT, get_format
from app.services.ai.gemini_service import gemini_service
from app.services.ai.prompt_manager import prompt_manager
from app.services.ai.response_parser import ResponseParseError, parse_into
from app.services.intelligence.patterns import patterns_summary_text

log = get_logger("trendforge.ai.analyzer")

Builder = Callable[[Session, Trend, dict, str, dict], dict]


class TrendNotFoundError(Exception):
    pass


# --- helpers --------------------------------------------------------------

def _iso(dt: datetime | None) -> str:
    if dt is None:
        return "unknown"
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=UTC)
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


# --- Sprint 5 builders ----------------------------------------------------

def _competitor_titles(session: Session, limit: int = 25) -> str:
    rows = session.exec(
        select(CompetitorVideo).order_by(CompetitorVideo.views.desc()).limit(limit)
    ).all()
    if not rows:
        return "(no competitor data collected)"
    return "\n".join(f"- {v.title}" for v in rows if v.title)


def _previously_used(session: Session, limit: int = 30) -> str:
    """Gather previously generated idea/hook texts for duplicate protection."""
    used: list[str] = []
    rows = session.exec(
        select(GeneratedContent).where(
            GeneratedContent.kind.in_(["strategy", "multi_ideas", "hooks"])
        )
    ).all()
    for row in rows:
        data = (row.payload or {}).get("data", {})
        for item in data.get("shorts", []) + data.get("long_videos", []):
            if isinstance(item, dict) and item.get("idea"):
                used.append(item["idea"])
        for hook in data.get("hooks", []):
            if isinstance(hook, dict) and hook.get("text"):
                used.append(hook["text"])
        if len(used) >= limit:
            break
    return "\n".join(f"- {u}" for u in used[:limit]) if used else ""


def _b_forecast(session, trend, params, variant, base):
    base["existing_coverage"] = _related_headlines(session, trend)
    return base


def _b_upload_advisor(session, trend, params, variant, base):
    base["competitor_patterns"] = patterns_summary_text()
    return base


def _b_competitor_gap(session, trend, params, variant, base):
    base["competitor_titles"] = _competitor_titles(session)
    return base


def _b_multi_ideas(session, trend, params, variant, base):
    avoid = "" if params.get("_force") else _previously_used(session)
    base["avoid_list"] = avoid or "(none yet)"
    return base


def _project_assets(session: Session, trend_id: int, variant: str) -> str:
    """Compact JSON of every generated module for a project (for review)."""
    rows = session.exec(
        select(GeneratedContent)
        .where(GeneratedContent.trend_id == trend_id)
        .where(GeneratedContent.variant == variant)
        .where(GeneratedContent.kind != "quality_review")
    ).all()
    if not rows:
        return "(nothing generated yet)"
    assets = {r.kind: (r.payload or {}).get("data", {}) for r in rows}
    return json.dumps(assets, ensure_ascii=False, default=str)[:24000]


def _b_quality_review(session, trend, params, variant, base):
    base = _with_format(params, base)
    base["assets"] = _project_assets(session, trend.id, variant)
    return base


def _b_research(session, trend, params, variant, base):
    from app.services.research import engine as research_engine

    pkg = research_engine.get_base(trend.id) or {}
    members = pkg.get("members", [])
    sources = [
        {"source": s["source"], "tier": s.get("tier_label"), "count": s["count"]}
        for s in pkg.get("sources", [])[:15]
    ]
    timeline = [
        {"time": e["time"], "source": e["source"]} for e in pkg.get("timeline", [])[:25]
    ]
    base["research_sources"] = _json(sources)
    base["research_timeline"] = _json(timeline)
    base["research_cluster"] = "\n".join(f"- {m['title']}" for m in members[:30]) or "(no cluster)"
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
    # Sprint 5 — creator intelligence
    "forecast": GenSpec("forecast", TrendForecast, _b_forecast),
    "upload_advisor": GenSpec("upload_advisor", UploadAdvice, _b_upload_advisor),
    "competitor_gap": GenSpec("competitor_gap", CompetitorGap, _b_competitor_gap),
    "multi_ideas": GenSpec("multi_ideas", MultiIdeas, _b_multi_ideas),
    # Sprint 6 — quality review (format-scoped, aggregates the project)
    "quality_review": GenSpec("quality_review", QualityReview, _b_quality_review, uses_variant=True),
    # Sprint 7 — AI research verification
    "research": GenSpec("research", ResearchAI, _b_research),
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


# How many times to regenerate when the model returns unparseable JSON.
PARSE_RETRIES = 2


async def _generate_and_parse(rendered: str, template, spec, kind: str):
    """Call the model and parse its response, regenerating on parse failure.

    Models occasionally emit malformed JSON. A fresh generation usually
    succeeds, so retry parse failures before giving up.
    """
    last_exc: ResponseParseError | None = None
    for attempt in range(1, PARSE_RETRIES + 1):
        raw = await gemini_service.generate_json(
            rendered, temperature=template.temperature, label=kind
        )
        try:
            return raw, parse_into(raw, spec.schema)
        except ResponseParseError as exc:
            last_exc = exc
            log_ai(
                "response parse failed",
                kind=kind,
                attempt=attempt,
                retrying=attempt < PARSE_RETRIES,
                error=str(exc),
            )
    assert last_exc is not None
    raise last_exc


async def generate(
    trend_id: int,
    kind: str,
    *,
    params: dict | None = None,
    force: bool = False,
    job_id: str | None = None,
) -> dict:
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

        context = spec.builder(
            session, trend, {**params, "_force": force}, variant, _base_context(trend)
        )
        trend_title = trend.title

    rendered, template = prompt_manager.render(spec.prompt, context)

    start = time.perf_counter()
    raw, model = await _generate_and_parse(rendered, template, spec, kind)
    generation_ms = int((time.perf_counter() - start) * 1000)
    data = model.model_dump()

    now = datetime.now(UTC)
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
        session.add(
            GenerationLog(
                job_id=job_id,
                trend_id=trend_id,
                kind=kind,
                variant=variant,
                prompt_version=template.version,
                prompt_text=rendered,
                response=data,
                prompt_chars=len(rendered),
                response_chars=len(raw),
                duration_ms=generation_ms,
                cached=False,
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
