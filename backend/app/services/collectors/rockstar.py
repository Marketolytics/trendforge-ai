"""Rockstar Newswire collector.

Rockstar's Newswire is consumed via its RSS feed (configured per source). It's
an RSS specialization so it stays reliable and never scrapes raw HTML.
"""

from __future__ import annotations

from app.services.collectors.rss import RSSCollector


class RockstarCollector(RSSCollector):
    type = "rockstar"

    def __init__(self, **kwargs) -> None:
        kwargs.setdefault("category", "gaming")
        super().__init__(**kwargs)
