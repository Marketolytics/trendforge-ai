"""RSS / Atom collector.

Reliable, dependency-light and the backbone for gaming news, developer blogs,
YouTube channel feeds and Google Trends' RSS endpoint. Supports multiple feeds
per source, tolerates malformed feeds, and de-duplicates within a run.
"""

from __future__ import annotations

import asyncio
import re
from datetime import datetime, timezone
from time import mktime, struct_time
from typing import Any

import feedparser

from app.core.logging import get_logger, log_network_error
from app.services.collectors.base import BaseCollector, StandardTrend
from app.services.collectors.net import fetch_text

log = get_logger("trendforge.collector.rss")
_IMG_RE = re.compile(r'<img[^>]+src="([^"]+)"', re.IGNORECASE)
_TAG_RE = re.compile(r"<[^>]+>")


def _struct_to_dt(value: struct_time | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromtimestamp(mktime(value), tz=timezone.utc)
    except (OverflowError, ValueError):
        return None


def _strip_html(text: str | None) -> str | None:
    if not text:
        return None
    cleaned = _TAG_RE.sub("", text)
    return re.sub(r"\s+", " ", cleaned).strip() or None


def _extract_image(entry: Any) -> str | None:
    media = entry.get("media_content") or entry.get("media_thumbnail")
    if media and isinstance(media, list) and media[0].get("url"):
        return media[0]["url"]
    for enc in entry.get("enclosures", []) or []:
        if str(enc.get("type", "")).startswith("image"):
            return enc.get("href")
    summary = entry.get("summary", "")
    match = _IMG_RE.search(summary)
    return match.group(1) if match else None


class RSSCollector(BaseCollector):
    """Collect items from one or more RSS/Atom feeds.

    Config:
        feeds: list[str]   - feed URLs (or use ``url`` for a single feed)
        limit: int         - max items per feed (default 25)
        language / region  - metadata overrides
    """

    type = "rss"

    @property
    def _feeds(self) -> list[str]:
        feeds = self.config.get("feeds")
        if isinstance(feeds, list) and feeds:
            return feeds
        single = self.config.get("url")
        return [single] if single else []

    async def collect(self) -> list[StandardTrend]:
        limit = int(self.config.get("limit", 25))
        results: dict[str, StandardTrend] = {}

        for feed_url in self._feeds:
            try:
                raw = await fetch_text(feed_url)
            except Exception as exc:  # noqa: BLE001
                log_network_error(self.name, feed_url, exc)
                continue

            parsed = await asyncio.to_thread(feedparser.parse, raw)
            if getattr(parsed, "bozo", 0) and not parsed.entries:
                log.warning(
                    "invalid or empty feed",
                    extra={"category": "network", "url": feed_url, "source": self.name},
                )
                continue

            for entry in parsed.entries[:limit]:
                trend = self._to_trend(entry)
                if trend is not None:
                    results[trend.content_hash] = trend  # dedupe within source

        return list(results.values())

    def _to_trend(self, entry: Any) -> StandardTrend | None:
        title = (entry.get("title") or "").strip()
        if not title:
            return None

        published = _struct_to_dt(
            entry.get("published_parsed") or entry.get("updated_parsed")
        )
        summary = _strip_html(entry.get("summary") or entry.get("description"))

        trend = StandardTrend(
            title=title,
            summary=summary,
            url=entry.get("link"),
            source=self.name,
            source_type=self.type,
            published_time=published,
            category=self.category,
            image_url=_extract_image(entry),
            language=self.config.get("language", "en"),
            region=self.config.get("region", "US"),
            raw_content=summary,
            source_id=self.source_id,
        )
        trend.ensure_keywords()
        return trend
