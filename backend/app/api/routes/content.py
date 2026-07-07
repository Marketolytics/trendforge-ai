"""Content generation status.

Content generation is delivered by the AI content factory under ``/api/ai``
(single modules, full package, and export). This endpoint reports what content
generation is currently available so clients can discover capabilities.
"""

from __future__ import annotations

from fastapi import APIRouter

from app.services.ai.formats import DEFAULT_FORMAT, FORMATS
from app.services.ai.gemini_service import gemini_service

router = APIRouter(prefix="/content", tags=["content"])

# Content-production module kinds produced by the content factory.
CONTENT_MODULES = [
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


@router.get("/status")
def content_status() -> dict:
    """Report content-generation availability and capabilities."""
    return {
        "available": True,
        "configured": gemini_service.is_configured,
        "model": gemini_service.model(),
        "modules": CONTENT_MODULES,
        "formats": [f.key for f in FORMATS.values()],
        "default_format": DEFAULT_FORMAT,
        "generate_endpoint": "/api/ai/package/{trend_id}",
        "export_endpoint": "/api/ai/export/{trend_id}",
    }
