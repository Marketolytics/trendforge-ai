"""AI intelligence endpoints.

Each endpoint returns a standard :class:`AIEnvelope`. Results are persisted and
reused; pass ``force=true`` to regenerate.
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query

from app.schemas.ai import AIEnvelope, AIStatus, PromptInfo
from app.services.ai import analyzer
from app.services.ai.gemini_service import (
    AIGenerationError,
    AINotConfiguredError,
    gemini_service,
)
from app.services.ai.prompt_manager import prompt_manager
from app.services.ai.response_parser import ResponseParseError

router = APIRouter(prefix="/ai", tags=["ai"])


async def _run(coro) -> AIEnvelope:
    """Execute an analyzer coroutine, mapping domain errors to HTTP."""
    try:
        result = await coro
        return AIEnvelope(**result)
    except analyzer.TrendNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except AINotConfiguredError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except (AIGenerationError, ResponseParseError) as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@router.get("/status", response_model=AIStatus)
def ai_status() -> AIStatus:
    return AIStatus(configured=gemini_service.is_configured, model=gemini_service.model())


@router.get("/prompts", response_model=list[PromptInfo])
def list_prompts() -> list[PromptInfo]:
    return [PromptInfo(**p) for p in prompt_manager.list_templates()]


@router.post("/analyze/{trend_id}", response_model=AIEnvelope)
async def analyze_trend(trend_id: int, force: bool = Query(False)) -> AIEnvelope:
    return await _run(analyzer.generate(trend_id, "analysis", force=force))


@router.post("/summary/{trend_id}", response_model=AIEnvelope)
async def generate_summary(trend_id: int, force: bool = Query(False)) -> AIEnvelope:
    return await _run(analyzer.generate(trend_id, "summary", force=force))


@router.post("/opportunity/{trend_id}", response_model=AIEnvelope)
async def generate_opportunity(trend_id: int, force: bool = Query(False)) -> AIEnvelope:
    return await _run(analyzer.get_opportunity(trend_id, force=force))


@router.post("/strategy/{trend_id}", response_model=AIEnvelope)
async def generate_strategy(trend_id: int, force: bool = Query(False)) -> AIEnvelope:
    return await _run(analyzer.generate(trend_id, "strategy", force=force))


@router.post("/hooks/{trend_id}", response_model=AIEnvelope)
async def generate_hooks(trend_id: int, force: bool = Query(False)) -> AIEnvelope:
    return await _run(analyzer.generate(trend_id, "hooks", force=force))


@router.post("/titles/{trend_id}", response_model=AIEnvelope)
async def generate_titles(trend_id: int, force: bool = Query(False)) -> AIEnvelope:
    return await _run(analyzer.generate(trend_id, "titles", force=force))


@router.post("/thumbnail/{trend_id}", response_model=AIEnvelope)
async def generate_thumbnail(trend_id: int, force: bool = Query(False)) -> AIEnvelope:
    return await _run(analyzer.generate(trend_id, "thumbnail", force=force))
