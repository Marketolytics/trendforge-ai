"""Shared API response schemas."""

from __future__ import annotations

from datetime import UTC, datetime

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    """Backend liveness/readiness payload."""

    status: str = "ok"
    app: str
    version: str
    database: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))


class MessageResponse(BaseModel):
    """Generic message envelope."""

    message: str
