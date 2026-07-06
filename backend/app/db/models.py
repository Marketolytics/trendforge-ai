"""Core database models.

Milestone 1 defines the foundational tables so the schema initializes on
startup. Collector/scoring/generator fields are expanded in later milestones.
"""

from __future__ import annotations

from datetime import datetime, timezone

from sqlmodel import Field, SQLModel


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Trend(SQLModel, table=True):
    """A trending topic collected from a source."""

    __tablename__ = "trends"

    id: int | None = Field(default=None, primary_key=True)
    title: str = Field(index=True)
    source: str = Field(index=True, description="e.g. youtube, reddit, rss, steam")
    url: str | None = None
    summary: str | None = None
    score: float = Field(default=0.0, description="Overall trend score 0-100")
    created_at: datetime = Field(default_factory=_utcnow, index=True)


class ContentProject(SQLModel, table=True):
    """A generated content package tied to a trend."""

    __tablename__ = "content_projects"

    id: int | None = Field(default=None, primary_key=True)
    trend_id: int | None = Field(default=None, foreign_key="trends.id", index=True)
    title: str
    status: str = Field(default="draft", description="draft | generated | exported")
    created_at: datetime = Field(default_factory=_utcnow, index=True)


class Setting(SQLModel, table=True):
    """Key/value application settings persisted locally."""

    __tablename__ = "settings"

    key: str = Field(primary_key=True)
    value: str = Field(default="")
    updated_at: datetime = Field(default_factory=_utcnow)
