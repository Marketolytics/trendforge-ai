"""YouTube collector.

YouTube exposes a per-channel Atom feed (no API key). This reuses the RSS
pipeline and enriches items with view counts where the feed provides them.
"""

from __future__ import annotations

from typing import Any

from app.services.collectors.base import StandardTrend
from app.services.collectors.rss import RSSCollector

CHANNEL_FEED = "https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"


class YouTubeCollector(RSSCollector):
    """Collect recent uploads from configured channels.

    Config:
        channels: list[str] - channel IDs (UC...)
        limit: int          - items per channel (default 15)
    """

    type = "youtube"

    @property
    def _feeds(self) -> list[str]:
        channels = self.config.get("channels") or []
        if isinstance(channels, str):
            channels = [channels]
        return [CHANNEL_FEED.format(channel_id=c) for c in channels]

    def _to_trend(self, entry: Any) -> StandardTrend | None:
        trend = super()._to_trend(entry)
        if trend is None:
            return None
        trend.source_type = self.type
        # Views come through the media:community namespace when available.
        stats = entry.get("media_statistics") or {}
        views = stats.get("views")
        if views:
            try:
                trend.popularity_score = float(views)
            except (TypeError, ValueError):
                pass
        # Prefer the video thumbnail.
        thumb = entry.get("media_thumbnail")
        if thumb and isinstance(thumb, list) and thumb[0].get("url"):
            trend.image_url = thumb[0]["url"]
        return trend
