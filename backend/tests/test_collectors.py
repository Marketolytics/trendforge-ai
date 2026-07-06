"""Collector parsing + normalization."""

from __future__ import annotations

import feedparser

from app.services.collectors.base import (
    StandardTrend,
    extract_keywords,
    normalize_title,
)
from app.services.collectors.rss import RSSCollector

SAMPLE_FEED = """<?xml version="1.0"?>
<rss version="2.0"><channel><title>Test</title>
<item>
  <title>GTA 6 Trailer 2 Drops Today</title>
  <link>https://example.com/a</link>
  <description>Rockstar releases the second trailer.</description>
  <pubDate>Mon, 06 Jul 2026 10:00:00 GMT</pubDate>
</item>
<item>
  <title></title>
  <link>https://example.com/empty</link>
</item>
</channel></rss>"""


def test_normalize_and_keywords():
    assert normalize_title("GTA 6: Trailer 2!") == "gta 6 trailer 2"
    kws = extract_keywords("GTA 6 trailer drops with new gameplay footage")
    assert "trailer" in kws and "gameplay" in kws


def test_content_hash_stable():
    a = StandardTrend(title="GTA 6 Trailer!", source="X")
    b = StandardTrend(title="gta 6 trailer", source="Y")
    assert a.content_hash == b.content_hash  # normalized dedupe key


def test_rss_collector_maps_entries():
    parsed = feedparser.parse(SAMPLE_FEED)
    collector = RSSCollector(name="Test", category="gaming")
    trends = [t for e in parsed.entries if (t := collector._to_trend(e))]
    assert len(trends) == 1  # the empty-title item is skipped
    trend = trends[0]
    assert trend.title == "GTA 6 Trailer 2 Drops Today"
    assert trend.source == "Test"
    assert trend.published_time is not None
    assert trend.keywords  # auto-extracted
