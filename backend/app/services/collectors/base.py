"""Collector base contract and the standardized trend schema.

Every collector normalizes its source into ``StandardTrend`` objects. Raw
site/API payloads never leave a collector unnormalized.
"""

from __future__ import annotations

import hashlib
import re
from abc import ABC, abstractmethod
from datetime import UTC, datetime

from pydantic import BaseModel, Field

# Very small English stopword set for lightweight keyword extraction.
_STOPWORDS = {
    "the", "a", "an", "and", "or", "but", "of", "to", "in", "on", "for", "with",
    "is", "are", "was", "were", "be", "been", "at", "by", "from", "as", "it",
    "this", "that", "these", "those", "new", "how", "why", "what", "will",
    "you", "your", "we", "our", "has", "have", "had", "not", "can", "get",
    "its", "into", "out", "up", "down", "off", "over", "all", "more", "now",
}
_WORD_RE = re.compile(r"[a-z0-9][a-z0-9\-']+")


def utcnow() -> datetime:
    return datetime.now(UTC)


def normalize_title(title: str) -> str:
    """Lowercase, strip punctuation and collapse whitespace for dedupe."""
    text = re.sub(r"[^a-z0-9\s]", " ", title.lower())
    return re.sub(r"\s+", " ", text).strip()


def extract_keywords(text: str, limit: int = 8) -> list[str]:
    """Cheap keyword extraction from a title/summary (no NLP deps)."""
    counts: dict[str, int] = {}
    for word in _WORD_RE.findall(text.lower()):
        if word in _STOPWORDS or len(word) < 3:
            continue
        counts[word] = counts.get(word, 0) + 1
    ranked = sorted(counts, key=lambda w: (-counts[w], w))
    return ranked[:limit]


class StandardTrend(BaseModel):
    """Common structure returned by every collector."""

    title: str
    summary: str | None = None
    url: str | None = None
    source: str
    source_type: str = "rss"
    published_time: datetime | None = None
    category: str = "general"
    keywords: list[str] = Field(default_factory=list)
    popularity_score: float = 0.0
    image_url: str | None = None
    language: str = "en"
    region: str = "US"
    raw_content: str | None = None
    collection_timestamp: datetime = Field(default_factory=utcnow)
    source_id: int | None = None

    # Aggregation metadata (populated by the aggregation engine).
    cluster_id: str | None = None
    cluster_size: int = 1
    score: float = 0.0

    @property
    def content_hash(self) -> str:
        """Stable dedupe key from the normalized title (+ url host)."""
        basis = normalize_title(self.title)
        return hashlib.sha1(basis.encode("utf-8")).hexdigest()

    def ensure_keywords(self) -> None:
        if not self.keywords:
            self.keywords = extract_keywords(f"{self.title} {self.summary or ''}")


class BaseCollector(ABC):
    """Abstract collector. Subclasses implement :meth:`collect`."""

    #: Machine-readable source type, e.g. ``"rss"`` or ``"reddit"``.
    type: str = "base"

    def __init__(
        self,
        *,
        name: str,
        category: str = "general",
        config: dict | None = None,
        source_id: int | None = None,
    ) -> None:
        self.name = name
        self.category = category
        self.config = config or {}
        self.source_id = source_id

    @abstractmethod
    async def collect(self) -> list[StandardTrend]:
        """Fetch and normalize trends. Must not raise on partial failure."""
        raise NotImplementedError

    def __repr__(self) -> str:  # pragma: no cover
        return f"<{self.__class__.__name__} name={self.name!r}>"
