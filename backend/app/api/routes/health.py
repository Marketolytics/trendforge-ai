"""Health / liveness endpoints."""

from __future__ import annotations

from fastapi import APIRouter
from sqlalchemy import text

from app.config import settings
from app.db.session import engine
from app.schemas.common import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    """Report backend status and database connectivity."""
    db_status = "connected"
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except Exception:  # noqa: BLE001 - report any failure as disconnected
        db_status = "disconnected"

    return HealthResponse(
        app=settings.app_name,
        version=settings.version,
        database=db_status,
    )
