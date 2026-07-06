"""Developer panel: stats, logs, prompt tools and generation history."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query
from sqlalchemy import func
from sqlmodel import Session, select

from app.config import settings
from app.db.models import (
    CompetitorVideo,
    GeneratedContent,
    GenerationLog,
    Job,
    Trend,
)
from app.db.session import engine
from app.services.ai import analyzer
from app.services.ai.prompt_manager import prompt_manager
from app.services.cache import cache
from app.services.orchestrator import engine as orchestrator

router = APIRouter(prefix="/dev", tags=["dev"])


def _count(session: Session, model) -> int:
    return int(session.scalar(select(func.count()).select_from(model)) or 0)


@router.get("/stats")
def dev_stats() -> dict:
    with Session(engine) as s:
        db = {
            "trends": _count(s, Trend),
            "generated_content": _count(s, GeneratedContent),
            "competitor_videos": _count(s, CompetitorVideo),
            "jobs": _count(s, Job),
            "generation_log": _count(s, GenerationLog),
        }
    return {
        "cache": cache.stats(),
        "queue": orchestrator.queue_stats(),
        "db": db,
        "prompts": prompt_manager.list_templates(),
        "model": settings.version,
    }


@router.get("/logs")
def dev_logs(lines: int = Query(100, ge=1, le=1000)) -> dict:
    log_path = settings.resolved_log_dir / "trendforge.log"
    if not log_path.exists():
        return {"lines": []}
    with log_path.open("r", encoding="utf-8", errors="ignore") as f:
        tail = f.readlines()[-lines:]
    return {"lines": [ln.rstrip("\n") for ln in tail]}


@router.get("/prompts/{name}")
def get_prompt(name: str) -> dict:
    try:
        tpl = prompt_manager.get(name)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Prompt not found") from exc
    return {
        "name": tpl.name,
        "version": tpl.version,
        "description": tpl.description,
        "temperature": tpl.temperature,
        "variables": prompt_manager.variables(name),
        "body": tpl.body,
    }


@router.post("/prompts/{name}/preview")
def preview_prompt(name: str, trend_id: int = Query(...), format: str = Query("60s")) -> dict:
    with Session(engine) as s:
        trend = s.get(Trend, trend_id)
        if trend is None:
            raise HTTPException(status_code=404, detail="Trend not found")
        context = analyzer._base_context(trend)

    from app.services.ai.formats import get_format

    fmt = get_format(format)
    context.update(
        format_label=fmt.label,
        seconds=fmt.seconds,
        scene_hint=fmt.scene_hint,
        voice_style="Professional",
        existing_coverage="(sample related coverage)",
        competitor_titles="(sample competitor titles)",
        competitor_patterns="(sample competitor patterns)",
        avoid_list="(sample avoid list)",
        script="(sample script JSON)",
        storyboard="(sample storyboard JSON)",
        continuity="(sample continuity bible JSON)",
        assets="(sample generated assets JSON)",
        previous_scene="",
    )
    try:
        validation = prompt_manager.validate(name, context)
        rendered = prompt_manager.get(name).render(context)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Prompt not found") from exc
    return {**validation, "rendered": rendered}


@router.get("/generations")
def list_generations(
    trend_id: int | None = Query(None),
    kind: str | None = Query(None),
    limit: int = Query(50, ge=1, le=200),
) -> list[dict]:
    with Session(engine) as s:
        stmt = select(GenerationLog)
        if trend_id is not None:
            stmt = stmt.where(GenerationLog.trend_id == trend_id)
        if kind:
            stmt = stmt.where(GenerationLog.kind == kind)
        stmt = stmt.order_by(GenerationLog.created_at.desc()).limit(limit)
        rows = s.exec(stmt).all()
    return [
        {
            "id": r.id,
            "trend_id": r.trend_id,
            "kind": r.kind,
            "variant": r.variant,
            "prompt_version": r.prompt_version,
            "prompt_chars": r.prompt_chars,
            "response_chars": r.response_chars,
            "duration_ms": r.duration_ms,
            "created_at": r.created_at.isoformat() if r.created_at else None,
        }
        for r in rows
    ]


@router.get("/generations/{gen_id}")
def get_generation(gen_id: int) -> dict:
    with Session(engine) as s:
        row = s.get(GenerationLog, gen_id)
        if row is None:
            raise HTTPException(status_code=404, detail="Generation not found")
        return {
            "id": row.id,
            "trend_id": row.trend_id,
            "kind": row.kind,
            "variant": row.variant,
            "prompt_version": row.prompt_version,
            "prompt_text": row.prompt_text,
            "response": row.response,
            "duration_ms": row.duration_ms,
            "created_at": row.created_at.isoformat() if row.created_at else None,
        }
