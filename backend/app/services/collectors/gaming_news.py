"""Gaming news collector.

A thin specialization of the RSS collector for major gaming outlets. Kept as
its own type so it can be enabled/filtered independently and evolve its own
enrichment later (e.g. outlet authority weighting).
"""

from __future__ import annotations

from app.services.collectors.rss import RSSCollector


class GamingNewsCollector(RSSCollector):
    type = "gaming_news"

    def __init__(self, **kwargs) -> None:
        kwargs.setdefault("category", "gaming")
        super().__init__(**kwargs)
