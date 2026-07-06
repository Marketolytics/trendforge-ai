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

from datetime import UTC, datetime

from sqlalchemy import JSON, Column, Text
from sqlmodel import Field, SQLModel


def utcnow() -> datetime:
    return datetime.now(UTC)


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
    """An AI-generated module tied to a trend.

    A "content package" is the set of rows sharing a (trend_id, variant), where
    ``variant`` is the chosen format/duration (e.g. "60s", "5min"). ``kind`` is
    the module (script, storyboard, image_prompts, ...).
    """

    __tablename__ = "generated_content"

    id: int | None = Field(default=None, primary_key=True)
    trend_id: int | None = Field(default=None, foreign_key="trends.id", index=True)
    title: str
    kind: str = Field(default="package", index=True)
    variant: str = Field(default="", index=True, description="Format/duration key")
    payload: dict = Field(default_factory=dict, sa_column=Column(JSON))
    params: dict = Field(default_factory=dict, sa_column=Column(JSON))
    prompt_version: str = Field(default="")
    generation_ms: int = Field(default=0)
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


class CompetitorChannel(SQLModel, table=True):
    """A saved YouTube channel to track for competitive analysis."""

    __tablename__ = "competitor_channels"

    id: int | None = Field(default=None, primary_key=True)
    channel_id: str = Field(index=True, description="YouTube UC... channel id")
    name: str = Field(index=True)
    handle: str = Field(default="", description="Original @handle or URL provided")
    thumbnail: str | None = None
    category: str = Field(default="general", index=True)
    video_count: int = Field(default=0)
    last_refreshed: datetime | None = Field(default=None)
    created_at: datetime = Field(default_factory=utcnow, index=True)


class CompetitorVideo(SQLModel, table=True):
    """A video collected from a tracked competitor channel."""

    __tablename__ = "competitor_videos"

    id: int | None = Field(default=None, primary_key=True)
    channel_pk: int = Field(foreign_key="competitor_channels.id", index=True)
    video_id: str = Field(index=True)
    title: str
    url: str | None = None
    thumbnail: str | None = None
    published: datetime | None = Field(default=None, index=True)
    views: int = Field(default=0, index=True)
    likes: int | None = None
    comments: int | None = None
    duration_seconds: int | None = None
    category: str = Field(default="general")
    collected_at: datetime = Field(default_factory=utcnow)


class Favorite(SQLModel, table=True):
    """A user-saved item (trend, script, prompt, hook, thumbnail, seo, ...)."""

    __tablename__ = "favorites"

    id: int | None = Field(default=None, primary_key=True)
    type: str = Field(index=True, description="trend | script | prompt | hook | thumbnail | seo")
    label: str = Field(index=True)
    ref_id: int | None = Field(default=None, description="Related trend/content id")
    payload: dict = Field(default_factory=dict, sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=utcnow, index=True)


class ResearchPackage(SQLModel, table=True):
    """A deterministic research base package for a trend/story.

    ``base`` holds source-confidence, story cluster, timeline, keywords,
    entities and graph (all computed without AI). AI enrichment (facts,
    verification, summaries) is stored separately in ``generated_content``
    under kind ``research`` and merged on read.
    """

    __tablename__ = "research_packages"

    id: int | None = Field(default=None, primary_key=True)
    trend_id: int = Field(index=True)
    title: str
    base: dict = Field(default_factory=dict, sa_column=Column(JSON))
    confidence: float = Field(default=0.0)
    source_count: int = Field(default=0)
    created_at: datetime = Field(default_factory=utcnow, index=True)
    updated_at: datetime = Field(default_factory=utcnow)


class Job(SQLModel, table=True):
    """A background workflow job coordinated by the orchestrator."""

    __tablename__ = "jobs"

    id: str = Field(primary_key=True, description="uuid")
    workflow: str = Field(index=True)
    trend_id: int | None = Field(default=None, index=True)
    variant: str = Field(default="")
    params: dict = Field(default_factory=dict, sa_column=Column(JSON))
    priority: int = Field(default=5, index=True, description="lower = higher priority")
    status: str = Field(default="queued", index=True, description="queued|running|paused|completed|failed|cancelled")
    progress: float = Field(default=0.0)
    current_step: str = Field(default="")
    steps: list = Field(default_factory=list, sa_column=Column(JSON))
    result: dict = Field(default_factory=dict, sa_column=Column(JSON))
    error: str | None = None
    eta_seconds: int | None = None
    created_at: datetime = Field(default_factory=utcnow, index=True)
    updated_at: datetime = Field(default_factory=utcnow)
    started_at: datetime | None = None
    finished_at: datetime | None = None


class GenerationLog(SQLModel, table=True):
    """Append-only log of AI generations (for response history + compare)."""

    __tablename__ = "generation_log"

    id: int | None = Field(default=None, primary_key=True)
    job_id: str | None = Field(default=None, index=True)
    trend_id: int | None = Field(default=None, index=True)
    kind: str = Field(index=True)
    variant: str = Field(default="")
    prompt_version: str = Field(default="")
    prompt_text: str | None = Field(default=None, sa_column=Column(Text))
    response: dict = Field(default_factory=dict, sa_column=Column(JSON))
    prompt_chars: int = Field(default=0)
    response_chars: int = Field(default=0)
    duration_ms: int = Field(default=0)
    cached: bool = Field(default=False)
    created_at: datetime = Field(default_factory=utcnow, index=True)


class CachedRequest(SQLModel, table=True):
    """A cached HTTP / API response keyed by a stable request signature."""

    __tablename__ = "cached_requests"

    key: str = Field(primary_key=True)
    namespace: str = Field(default="http", index=True)
    value: str = Field(default="", sa_column=Column(Text))
    created_at: datetime = Field(default_factory=utcnow)
    expires_at: datetime = Field(index=True)
