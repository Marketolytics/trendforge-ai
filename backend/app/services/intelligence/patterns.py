"""Viral pattern analysis.

Computes recurring patterns across collected competitor videos: view stats,
top performers, upload-day/hour distribution, title keywords and publishing
frequency. Pure aggregation — no AI required.
"""

from __future__ import annotations

import re
import statistics
from collections import Counter
from datetime import UTC

from sqlmodel import Session, select

from app.db.models import CompetitorVideo
from app.db.session import engine
from app.services.collectors.base import extract_keywords

DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
_TITLE_CASE_RE = re.compile(r"\b[A-Z][A-Z0-9]{2,}\b")


def compute_patterns(channel_pk: int | None = None) -> dict:
    with Session(engine) as session:
        stmt = select(CompetitorVideo)
        if channel_pk is not None:
            stmt = stmt.where(CompetitorVideo.channel_pk == channel_pk)
        videos = list(session.exec(stmt).all())

    if not videos:
        return {"total_videos": 0}

    views = [v.views for v in videos if v.views]
    day_hist = Counter()
    hour_hist = Counter()
    published_dates = []
    title_words: Counter = Counter()
    caps_words: Counter = Counter()

    for v in videos:
        if v.published:
            pub = v.published if v.published.tzinfo else v.published.replace(tzinfo=UTC)
            day_hist[DAYS[pub.weekday()]] += 1
            hour_hist[pub.hour] += 1
            published_dates.append(pub)
        for kw in extract_keywords(v.title, limit=6):
            title_words[kw] += 1
        for caps in _TITLE_CASE_RE.findall(v.title):
            caps_words[caps] += 1

    top_videos = sorted(videos, key=lambda v: v.views, reverse=True)[:5]

    frequency_per_week = None
    if len(published_dates) >= 2:
        span_days = (max(published_dates) - min(published_dates)).days or 1
        frequency_per_week = round(len(published_dates) / (span_days / 7 or 1), 1)

    best_day = day_hist.most_common(1)[0][0] if day_hist else None
    best_hour = hour_hist.most_common(1)[0][0] if hour_hist else None

    return {
        "total_videos": len(videos),
        "avg_views": int(statistics.mean(views)) if views else 0,
        "median_views": int(statistics.median(views)) if views else 0,
        "max_views": max(views) if views else 0,
        "top_videos": [
            {"title": v.title, "views": v.views, "url": v.url, "thumbnail": v.thumbnail}
            for v in top_videos
        ],
        "upload_days": {d: day_hist.get(d, 0) for d in DAYS},
        "upload_hours": {str(h): hour_hist.get(h, 0) for h in range(24)},
        "best_day": best_day,
        "best_hour": best_hour,
        "frequency_per_week": frequency_per_week,
        "title_keywords": [{"word": w, "count": c} for w, c in title_words.most_common(15)],
        "common_caps_words": [{"word": w, "count": c} for w, c in caps_words.most_common(8)],
    }


def patterns_summary_text(channel_pk: int | None = None) -> str:
    """A compact, human/AI-readable summary of competitor patterns."""
    p = compute_patterns(channel_pk)
    if p.get("total_videos", 0) == 0:
        return "No competitor data collected yet."
    kws = ", ".join(k["word"] for k in p.get("title_keywords", [])[:8])
    return (
        f"{p['total_videos']} videos analyzed. Avg views {p['avg_views']:,}. "
        f"Best upload day: {p.get('best_day')}, best hour: {p.get('best_hour')}h. "
        f"~{p.get('frequency_per_week')} uploads/week. "
        f"Frequent title keywords: {kws}."
    )
