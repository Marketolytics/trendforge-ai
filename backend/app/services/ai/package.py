"""Content package orchestration.

One click -> the full production package. Modules run in dependency order:
script first, then storyboard + continuity, then everything that depends on
them in parallel. Individual modules remain independently regenerable via the
analyzer; this just coordinates a full run.
"""

from __future__ import annotations

import asyncio

from sqlmodel import Session, select

from app.core.logging import get_logger, performance
from app.db.models import GeneratedContent
from app.db.session import engine
from app.services.ai import analyzer
from app.services.ai.formats import DEFAULT_FORMAT, get_format
from app.services.ai.gemini_service import AINotConfiguredError

log = get_logger("trendforge.ai.package")


async def _safe(trend_id: int, kind: str, params: dict, force: bool) -> tuple[str, dict | None, str | None]:
    try:
        env = await analyzer.generate(trend_id, kind, params=params, force=force)
        return kind, env, None
    except AINotConfiguredError:
        raise  # fail fast: without a key nothing can be generated -> 409
    except Exception as exc:  # noqa: BLE001 - collect per-module failures
        log.warning("package module failed", extra={"category": "ai", "kind": kind, "error": str(exc)})
        return kind, None, str(exc)


async def generate_package(
    trend_id: int, *, format_key: str = DEFAULT_FORMAT, voice_style: str = "Professional", force: bool = False
) -> dict:
    """Generate every module for a trend/format package."""
    fmt = get_format(format_key)
    params = {"format": fmt.key, "voice_style": voice_style}
    modules: dict[str, dict] = {}
    failures: list[dict] = []

    def record(kind: str, env: dict | None, err: str | None) -> None:
        if env is not None:
            modules[kind] = env
        if err is not None:
            failures.append({"kind": kind, "error": err})

    with performance("package:generate", trend_id=trend_id, format=fmt.key):
        # 1) Script (foundation).
        record(*await _safe(trend_id, "script", params, force))

        # 2) Storyboard + continuity (depend on script).
        for res in await asyncio.gather(
            _safe(trend_id, "storyboard", params, force),
            _safe(trend_id, "continuity", params, force),
        ):
            record(*res)

        # 3) Everything else, in parallel.
        rest = ["image_prompts", "video_prompts", "voiceover", "broll",
                "thumbnail_blueprint", "seo_package", "checklist"]
        for res in await asyncio.gather(*(_safe(trend_id, k, params, force) for k in rest)):
            record(*res)

    return {
        "trend_id": trend_id,
        "variant": fmt.key,
        "format": fmt.label,
        "modules": modules,
        "failures": failures,
    }


def get_package(trend_id: int, *, format_key: str = DEFAULT_FORMAT) -> dict:
    """Load whatever modules already exist for a trend/format."""
    fmt = get_format(format_key)
    modules: dict[str, dict] = {}
    with Session(engine) as session:
        rows = session.exec(
            select(GeneratedContent)
            .where(GeneratedContent.trend_id == trend_id)
            .where(GeneratedContent.variant == fmt.key)
        ).all()
        for row in rows:
            if not row.payload:
                continue
            modules[row.kind] = {
                "kind": row.kind,
                "trend_id": trend_id,
                "variant": fmt.key,
                "prompt_version": row.prompt_version,
                "cached": True,
                "generated_at": analyzer._iso(row.created_at),
                "generation_ms": row.generation_ms,
                "data": (row.payload or {}).get("data", {}),
            }
    return {"trend_id": trend_id, "variant": fmt.key, "format": fmt.label, "modules": modules}
