"""Trend API schemas."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class TrendOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    summary: str | None = None
    url: str | None = None
    source: str
    source_type: str
    published_time: datetime | None = None
    category: str
    keywords: list[str] = []
    popularity_score: float
    image_url: str | None = None
    language: str
    region: str
    cluster_size: int
    score: float
    collection_timestamp: datetime


class TrendDetail(TrendOut):
    raw_content: str | None = None
    content_hash: str
    cluster_id: str | None = None
    source_id: int | None = None
    created_at: datetime


class TrendListResponse(BaseModel):
    trends: list[TrendOut]
    count: int
    generated_at: datetime


class RefreshResponse(BaseModel):
    status: str
    trends_collected: int
    raw_items: int
    sources_ok: int
    sources_failed: int
    duration_ms: int
    failures: list[dict] = []
