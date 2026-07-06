"""Reddit collector.

Reddit blocks unauthenticated access to its ``.json`` endpoints (HTTP 403),
so we use the public per-subreddit RSS feed with a browser User-Agent, which
is reliable and requires no credentials.

RSS does not expose exact upvote/comment counts; hot-list rank is used as the
popularity signal. Exact engagement metrics require Reddit OAuth, which can be
added later as an optional, credentialed source.
"""

from __future__ import annotations

import asyncio

import feedparser

from app.core.logging import get_logger, log_network_error
from app.services.collectors.base import BaseCollector, StandardTrend, extract_keywords
from app.services.collectors.net import fetch_text
from app.services.collectors.rss import _extract_image, _strip_html, _struct_to_dt

log = get_logger("trendforge.collector.reddit")

FEED_URL = "https://www.reddit.com/r/{sub}/hot.rss"
# Reddit serves RSS to browser-like clients but blocks generic bot agents.
BROWSER_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
)


class RedditCollector(BaseCollector):
    """Collect hot posts from one or more subreddits via RSS.

    Config:
        subreddits: list[str] - subreddit names (without 'r/')
        limit: int            - posts per subreddit (default 20)
    """

    type = "reddit"

    async def collect(self) -> list[StandardTrend]:
        subs = self.config.get("subreddits") or []
        if isinstance(subs, str):
            subs = [subs]
        limit = int(self.config.get("limit", 20))

        trends: list[StandardTrend] = []
        for sub in subs:
            url = FEED_URL.format(sub=sub)
            try:
                raw = await fetch_text(url, headers={"User-Agent": BROWSER_UA})
            except Exception as exc:  # noqa: BLE001
                log_network_error(f"r/{sub}", url, exc)
                continue

            parsed = await asyncio.to_thread(feedparser.parse, raw)
            for index, entry in enumerate(parsed.entries[:limit]):
                trend = self._to_trend(entry, sub, index, limit)
                if trend is not None:
                    trends.append(trend)

        return trends

    def _to_trend(self, entry, sub: str, index: int, limit: int) -> StandardTrend | None:
        title = (entry.get("title") or "").strip()
        if not title:
            return None

        # Hot-rank proxy: higher position -> higher popularity signal.
        popularity = float(max(limit - index, 1))
        published = _struct_to_dt(
            entry.get("published_parsed") or entry.get("updated_parsed")
        )
        summary = _strip_html(entry.get("summary") or entry.get("content"))

        return StandardTrend(
            title=title,
            summary=(summary or f"Hot in r/{sub}.")[:500],
            url=entry.get("link"),
            source=f"r/{sub}",
            source_type=self.type,
            published_time=published,
            category=self.category,
            keywords=extract_keywords(title),
            popularity_score=popularity,
            image_url=_extract_image(entry),
            language="en",
            region="US",
            raw_content=(summary or "")[:2000] or None,
            source_id=self.source_id,
        )
