"""Steam news collector.

Uses Valve's public ISteamNews API (no key required) to pull recent news
items for a configured set of app IDs.
"""

from __future__ import annotations

import re
from datetime import UTC, datetime
from typing import Any

from app.core.logging import get_logger, log_network_error
from app.services.collectors.base import BaseCollector, StandardTrend, extract_keywords
from app.services.collectors.net import fetch_json

log = get_logger("trendforge.collector.steam")
_TAG_RE = re.compile(r"<[^>]+>|\[/?[a-z]+\]")

NEWS_URL = "https://api.steampowered.com/ISteamNews/GetNewsForApp/v2/"


class SteamCollector(BaseCollector):
    """Collect news for configured Steam apps.

    Config:
        apps: list[{"appid": int, "name": str}]  - games to track
        count: int                               - items per app (default 8)
    """

    type = "steam"

    async def collect(self) -> list[StandardTrend]:
        apps = self.config.get("apps") or []
        count = int(self.config.get("count", 8))

        trends: list[StandardTrend] = []
        for app in apps:
            appid = app.get("appid")
            name = app.get("name", f"Steam App {appid}")
            if appid is None:
                continue
            try:
                data = await fetch_json(
                    NEWS_URL,
                    params={"appid": appid, "count": count, "maxlength": 600},
                )
            except Exception as exc:  # noqa: BLE001
                log_network_error(f"Steam:{name}", NEWS_URL, exc)
                continue

            items = (data or {}).get("appnews", {}).get("newsitems", [])
            for item in items:
                trend = self._to_trend(item, name)
                if trend is not None:
                    trends.append(trend)

        return trends

    def _to_trend(self, item: dict[str, Any], game: str) -> StandardTrend | None:
        title = (item.get("title") or "").strip()
        if not title:
            return None

        body = _TAG_RE.sub("", item.get("contents") or "").strip()
        date = item.get("date")
        published = datetime.fromtimestamp(date, tz=UTC) if date else None

        return StandardTrend(
            title=title,
            summary=body[:400] or None,
            url=item.get("url"),
            source=f"Steam · {game}",
            source_type=self.type,
            published_time=published,
            category=self.category,
            keywords=extract_keywords(f"{game} {title}"),
            popularity_score=0.0,
            language="en",
            region="US",
            raw_content=body[:2000] or None,
            source_id=self.source_id,
        )
