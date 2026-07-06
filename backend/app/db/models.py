"""Database models for TrendForge AI.

Six tables back the collection engine:
    trend_sources     - configured, data-driven collection sources
    trends            - normalized, deduplicated, scored trends
    generated_content - AI content packages (populated in a later sprint)
    history           - activity log of refresh runs
    settings          - persisted key/value user preferences
    cached_requests   - HTTP / API response cache with TTL
"""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import JSON, Column, Text
from sqlmodel import Field, SQLModel


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class TrendSource(SQLModel, table=True):
    """A configured collection source, driving which collectors run."""

    __tablename__ = "trend_sources"

    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    type: str = Field(index=True, description="rss | google_trends | reddit | steam | youtube")
    category: str = Field(default="general", index=True)
    # Collector-specific configuration (feed url, subreddit, appid, geo, ...).
    config: dict = Field(default_factory=dict, sa_column=Column(JSON))
    enabled: bool = Field(default=True, index=True)
    created_at: datetime = Field(default_factory=utcnow)


class Trend(SQLModel, table=True):
    """A normalized trending topic collected from a source."""

    __tablename__ = "trends"

    id: int | None = Field(default=None, primary_key=True)

    # --- Standard trend model --------------------------------------------
    title: str = Field(index=True)
    summary: str | None = Field(default=None, sa_column=Column(Text))
    url: str | None = Field(default=None)
    source: str = Field(index=True, description="Source name, e.g. 'IGN', 'r/gaming'")
    source_type: str = Field(default="rss", index=True)
    published_time: datetime | None = Field(default=None, index=True)
    category: str = Field(default="general", index=True)
    keywords: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    popularity_score: float = Field(default=0.0, description="Raw source popularity signal")
    image_url: str | None = None
    language: str = Field(default="en")
    region: str = Field(default="US")
    raw_content: str | None = Field(default=None, sa_column=Column(Text))
    collection_timestamp: datetime = Field(default_factory=utcnow, index=True)

    # --- Aggregation / dedupe metadata -----------------------------------
    source_id: int | None = Field(default=None, foreign_key="trend_sources.id", index=True)
    content_hash: str = Field(index=True, description="Dedupe key derived from title/url")
    cluster_id: str | None = Field(default=None, index=True)
    cluster_size: int = Field(default=1, description="How many near-duplicate stories merged")

    # Temporary preliminary score (real intelligence engine lands in Sprint 3).
    score: float = Field(default=0.0, index=True, description="Preliminary trend score 0-100")

    created_at: datetime = Field(default_factory=utcnow, index=True)


class GeneratedContent(SQLModel, table=True):
    """AI-generated content package tied to a trend (filled in a later sprint)."""

    __tablename__ = "generated_content"

    id: int | None = Field(default=None, primary_key=True)
    trend_id: int | None = Field(default=None, foreign_key="trends.id", index=True)
    title: str
    kind: str = Field(default="package", description="package | script | prompt | seo")
    payload: dict = Field(default_factory=dict, sa_column=Column(JSON))
    status: str = Field(default="draft", description="draft | generated | exported")
    created_at: datetime = Field(default_factory=utcnow, index=True)


class History(SQLModel, table=True):
    """Activity log of refresh runs and notable events."""

    __tablename__ = "history"

    id: int | None = Field(default=None, primary_key=True)
    event: str = Field(index=True, description="e.g. 'refresh'")
    status: str = Field(default="success", description="success | partial | error")
    trends_collected: int = Field(default=0)
    sources_ok: int = Field(default=0)
    sources_failed: int = Field(default=0)
    duration_ms: int = Field(default=0)
    detail: dict = Field(default_factory=dict, sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=utcnow, index=True)


class Setting(SQLModel, table=True):
    """Persisted key/value application settings."""

    __tablename__ = "settings"

    key: str = Field(primary_key=True)
    value: str = Field(default="", sa_column=Column(Text))
    updated_at: datetime = Field(default_factory=utcnow)


class CachedRequest(SQLModel, table=True):
    """A cached HTTP / API response keyed by a stable request signature."""

    __tablename__ = "cached_requests"

    key: str = Field(primary_key=True)
    namespace: str = Field(default="http", index=True)
    value: str = Field(default="", sa_column=Column(Text))
    created_at: datetime = Field(default_factory=utcnow)
    expires_at: datetime = Field(index=True)
