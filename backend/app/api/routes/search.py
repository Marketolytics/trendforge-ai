"""Global search endpoint."""

from __future__ import annotations

from fastapi import APIRouter, Query

from app.services import search_service

router = APIRouter(tags=["search"])


@router.get("/search")
def search(q: str = Query("", description="Search query")) -> dict:
    return {"query": q, "results": search_service.search(q)}
