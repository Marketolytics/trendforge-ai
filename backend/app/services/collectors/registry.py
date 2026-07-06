"""Collector registry.

Maps a source ``type`` to its collector class and builds collector instances
from ``TrendSource`` rows. Adding a new collector is a one-line registration.
"""

from __future__ import annotations

from app.core.logging import get_logger
from app.db.models import TrendSource
from app.services.collectors.base import BaseCollector
from app.services.collectors.gaming_news import GamingNewsCollector
from app.services.collectors.google_trends import GoogleTrendsCollector
from app.services.collectors.reddit import RedditCollector
from app.services.collectors.rockstar import RockstarCollector
from app.services.collectors.rss import RSSCollector
from app.services.collectors.steam import SteamCollector
from app.services.collectors.youtube import YouTubeCollector

log = get_logger("trendforge.collector.registry")

COLLECTOR_TYPES: dict[str, type[BaseCollector]] = {
    RSSCollector.type: RSSCollector,
    GoogleTrendsCollector.type: GoogleTrendsCollector,
    RedditCollector.type: RedditCollector,
    SteamCollector.type: SteamCollector,
    YouTubeCollector.type: YouTubeCollector,
    GamingNewsCollector.type: GamingNewsCollector,
    RockstarCollector.type: RockstarCollector,
}


def build_collector(source: TrendSource) -> BaseCollector | None:
    """Instantiate the collector for a source row, or ``None`` if unknown."""
    collector_cls = COLLECTOR_TYPES.get(source.type)
    if collector_cls is None:
        log.warning(
            "no collector for source type",
            extra={"category": "refresh", "type": source.type, "source": source.name},
        )
        return None
    return collector_cls(
        name=source.name,
        category=source.category,
        config=source.config or {},
        source_id=source.id,
    )
