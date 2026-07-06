"""AI intelligence + content factory endpoints.

Analysis and single-module generators return a standard :class:`AIEnvelope`.
Package endpoints coordinate a full run; export endpoints emit files.
Pass ``force=true`` to regenerate.
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import Response
from pydantic import BaseModel
from sqlmodel import Session

from app.db.models import Trend
from app.db.session import engine
from app.schemas.ai import AIEnvelope, AIStatus, PromptInfo
from app.services.ai import analyzer, package as package_service
from app.services.ai.export import export_single, export_zip
from app.services.ai.formats import DEFAULT_FORMAT, FORMATS, VOICE_STYLES
from app.services.ai.gemini_service import (
    AIGenerationError,
    AINotConfiguredError,
    gemini_service,
)
from app.services.ai.prompt_manager import prompt_manager
from app.services.ai.response_parser import ResponseParseError

router = APIRouter(prefix="/ai", tags=["ai"])


# --- error mapping --------------------------------------------------------

async def _run(coro) -> AIEnvelope:
    try:
        return AIEnvelope(**await coro)
    except analyzer.TrendNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except AINotConfiguredError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except (AIGenerationError, ResponseParseError) as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


def _params(format: str | None, voice_style: str | None = None) -> dict:
    params: dict = {}
    if format:
        params["format"] = format
    if voice_style:
        params["voice_style"] = voice_style
    return params


def _trend_title(trend_id: int) -> str:
    with Session(engine) as session:
        trend = session.get(Trend, trend_id)
        if trend is None:
            raise HTTPException(status_code=404, detail="Trend not found")
        return trend.title


# --- meta -----------------------------------------------------------------

@router.get("/status", response_model=AIStatus)
def ai_status() -> AIStatus:
    return AIStatus(configured=gemini_service.is_configured, model=gemini_service.model())


@router.get("/prompts", response_model=list[PromptInfo])
def list_prompts() -> list[PromptInfo]:
    return [PromptInfo(**p) for p in prompt_manager.list_templates()]


@router.get("/formats")
def list_formats() -> dict:
    return {
        "formats": [
            {"key": f.key, "label": f.label, "seconds": f.seconds, "kind": f.kind}
            for f in FORMATS.values()
        ],
        "voice_styles": VOICE_STYLES,
        "default": DEFAULT_FORMAT,
    }


# --- Sprint 3 analysis ----------------------------------------------------

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


# --- Sprint 4 content-factory modules -------------------------------------

@router.post("/script/{trend_id}", response_model=AIEnvelope)
async def generate_script(trend_id: int, format: str = Query(DEFAULT_FORMAT), force: bool = Query(False)):
    return await _run(analyzer.generate(trend_id, "script", params=_params(format), force=force))


@router.post("/storyboard/{trend_id}", response_model=AIEnvelope)
async def generate_storyboard(trend_id: int, format: str = Query(DEFAULT_FORMAT), force: bool = Query(False)):
    return await _run(analyzer.generate(trend_id, "storyboard", params=_params(format), force=force))


@router.post("/continuity/{trend_id}", response_model=AIEnvelope)
async def generate_continuity(trend_id: int, format: str = Query(DEFAULT_FORMAT), force: bool = Query(False)):
    return await _run(analyzer.generate(trend_id, "continuity", params=_params(format), force=force))


@router.post("/image-prompts/{trend_id}", response_model=AIEnvelope)
async def generate_image_prompts(trend_id: int, format: str = Query(DEFAULT_FORMAT), force: bool = Query(False)):
    return await _run(analyzer.generate(trend_id, "image_prompts", params=_params(format), force=force))


@router.post("/video-prompts/{trend_id}", response_model=AIEnvelope)
async def generate_video_prompts(trend_id: int, format: str = Query(DEFAULT_FORMAT), force: bool = Query(False)):
    return await _run(analyzer.generate(trend_id, "video_prompts", params=_params(format), force=force))


@router.post("/voiceover/{trend_id}", response_model=AIEnvelope)
async def generate_voiceover(
    trend_id: int,
    format: str = Query(DEFAULT_FORMAT),
    voice_style: str = Query("Professional"),
    force: bool = Query(False),
):
    return await _run(
        analyzer.generate(trend_id, "voiceover", params=_params(format, voice_style), force=force)
    )


@router.post("/broll/{trend_id}", response_model=AIEnvelope)
async def generate_broll(trend_id: int, format: str = Query(DEFAULT_FORMAT), force: bool = Query(False)):
    return await _run(analyzer.generate(trend_id, "broll", params=_params(format), force=force))


@router.post("/thumbnail-blueprint/{trend_id}", response_model=AIEnvelope)
async def generate_thumbnail_blueprint(trend_id: int, format: str = Query(DEFAULT_FORMAT), force: bool = Query(False)):
    return await _run(analyzer.generate(trend_id, "thumbnail_blueprint", params=_params(format), force=force))


@router.post("/seo/{trend_id}", response_model=AIEnvelope)
async def generate_seo(trend_id: int, format: str = Query(DEFAULT_FORMAT), force: bool = Query(False)):
    return await _run(analyzer.generate(trend_id, "seo_package", params=_params(format), force=force))


@router.post("/checklist/{trend_id}", response_model=AIEnvelope)
async def generate_checklist(trend_id: int, format: str = Query(DEFAULT_FORMAT), force: bool = Query(False)):
    return await _run(analyzer.generate(trend_id, "checklist", params=_params(format), force=force))


# --- Package --------------------------------------------------------------

class PackageResponse(BaseModel):
    trend_id: int
    variant: str
    format: str
    modules: dict[str, AIEnvelope]
    failures: list[dict] = []


@router.post("/package/{trend_id}", response_model=PackageResponse)
async def generate_package(
    trend_id: int,
    format: str = Query(DEFAULT_FORMAT),
    voice_style: str = Query("Professional"),
    force: bool = Query(False),
) -> PackageResponse:
    _trend_title(trend_id)  # 404 if missing
    try:
        result = await package_service.generate_package(
            trend_id, format_key=format, voice_style=voice_style, force=force
        )
    except AINotConfiguredError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    return PackageResponse(**result)


@router.get("/package/{trend_id}", response_model=PackageResponse)
def get_package(trend_id: int, format: str = Query(DEFAULT_FORMAT)) -> PackageResponse:
    result = package_service.get_package(trend_id, format_key=format)
    return PackageResponse(**result, failures=[])


# --- Export ---------------------------------------------------------------

@router.get("/export/{trend_id}/{kind}")
def export_module(
    trend_id: int,
    kind: str,
    format: str = Query(DEFAULT_FORMAT),
    fmt: str = Query("md", pattern="^(md|json)$"),
) -> Response:
    if kind not in analyzer.GENERATORS:
        raise HTTPException(status_code=404, detail="Unknown module kind")
    title = _trend_title(trend_id)
    result = package_service.get_package(trend_id, format_key=format)
    module = result["modules"].get(kind)
    if module is None:
        raise HTTPException(status_code=404, detail="Module not generated yet")
    filename, content, media_type = export_single(kind, module["data"], title, fmt)
    return Response(
        content=content,
        media_type=media_type,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/export/{trend_id}")
def export_package(trend_id: int, format: str = Query(DEFAULT_FORMAT)) -> Response:
    title = _trend_title(trend_id)
    result = package_service.get_package(trend_id, format_key=format)
    if not result["modules"]:
        raise HTTPException(status_code=404, detail="No modules generated for this format yet")
    filename, data = export_zip(title, result["format"], result["modules"])
    return Response(
        content=data,
        media_type="application/zip",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
