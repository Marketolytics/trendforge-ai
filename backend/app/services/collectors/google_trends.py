"""Google Trends collector.

Uses Google's public daily *trending searches* RSS endpoint, which needs no
API key and is stable. Traffic estimates (e.g. "2,000,000+") are parsed into a
raw popularity signal used for preliminary scoring.
"""

from __future__ import annotations

import asyncio
import re
from datetime import datetime, timezone
from time import mktime
from typing import Any

import feedparser

from app.core.logging import get_logger, log_network_error
from app.services.collectors.base import BaseCollector, StandardTrend, extract_keywords
from app.services.collectors.net import fetch_text

log = get_logger("trendforge.collector.google_trends")
_TRAFFIC_RE = re.compile(r"([\d,\.]+)\s*([kKmM]?)\+?")

RSS_URL = "https://trends.google.com/trending/rss?geo={geo}"


def _parse_traffic(value: str | None) -> float:
    """Turn '2,000,000+' or '20K+' into a float."""
    if not value:
        return 0.0
    match = _TRAFFIC_RE.search(value)
    if not match:
        return 0.0
    number = float(match.group(1).replace(",", ""))
    suffix = match.group(2).lower()
    if suffix == "k":
        number *= 1_000
    elif suffix == "m":
        number *= 1_000_000
    return number


class GoogleTrendsCollector(BaseCollector):
    """Collect trending searches for a region.

    Config:
        geo: str    - region code (default "US")
        limit: int  - max items (default 25)
    """

    type = "google_trends"

    async def collect(self) -> list[StandardTrend]:
        geo = self.config.get("geo", "US")
        limit = int(self.config.get("limit", 25))
        url = RSS_URL.format(geo=geo)

        try:
            raw = await fetch_text(url)
        except Exception as exc:  # noqa: BLE001
            log_network_error(self.name, url, exc)
            return []

        parsed = await asyncio.to_thread(feedparser.parse, raw)
        trends: list[StandardTrend] = []

        for entry in parsed.entries[:limit]:
            title = (entry.get("title") or "").strip()
            if not title:
                continue

            traffic_raw = (
                entry.get("ht_approx_traffic")
                or entry.get("approx_traffic")
                or _find_key(entry, "approx_traffic")
            )
            popularity = _parse_traffic(traffic_raw)

            published = None
            if entry.get("published_parsed"):
                try:
                    published = datetime.fromtimestamp(
                        mktime(entry["published_parsed"]), tz=timezone.utc
                    )
                except (OverflowError, ValueError):
                    published = None

            # Related news headlines enrich the summary when present.
            news_title = entry.get("ht_news_item_title") or _find_key(entry, "news_item_title")
            summary = f"Trending search. {news_title}" if news_title else "Trending search topic."

            trend = StandardTrend(
                title=title,
                summary=summary,
                url=entry.get("link"),
                source=self.name,
                source_type=self.type,
                published_time=published,
                category=self.category,
                keywords=extract_keywords(title),
                popularity_score=popularity,
                image_url=entry.get("ht_picture") or _find_key(entry, "picture"),
                region=geo,
                raw_content=traffic_raw,
                source_id=self.source_id,
            )
            trends.append(trend)

        return trends


def _find_key(entry: Any, needle: str) -> str | None:
    """Fallback: locate a namespaced key containing ``needle``."""
    for key, value in entry.items():
        if needle in key and isinstance(value, str):
            return value
    return None
