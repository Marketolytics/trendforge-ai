"""Content generation endpoints (placeholder for Milestone 1)."""

from __future__ import annotations

from fastapi import APIRouter

from app.schemas.common import MessageResponse

router = APIRouter(prefix="/content", tags=["content"])


@router.get("/status", response_model=MessageResponse)
def content_status() -> MessageResponse:
    """Report that content generation is not yet implemented."""
    return MessageResponse(message="Content generation available in a later milestone.")
