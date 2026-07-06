"""Preliminary trend scoring.

A lightweight, temporary score (0-100) so the UI can rank trends before the
full Trend Intelligence Engine arrives in Sprint 3. It blends freshness,
log-normalized popularity and corroboration (cluster size).
"""

from __future__ import annotations

import math
from datetime import datetime, timezone

from app.services.collectors.base import StandardTrend

# Component weights (must sum to 1.0).
W_FRESHNESS = 0.45
W_POPULARITY = 0.40
W_CORROBORATION = 0.15

FRESHNESS_WINDOW_HOURS = 72.0


def _hours_since(dt: datetime | None) -> float:
    if dt is None:
        return FRESHNESS_WINDOW_HOURS  # unknown age -> treat as stale-ish
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    delta = datetime.now(timezone.utc) - dt
    return max(delta.total_seconds() / 3600.0, 0.0)


def _freshness(dt: datetime | None) -> float:
    hours = _hours_since(dt)
    return max(0.0, 1.0 - hours / FRESHNESS_WINDOW_HOURS)


def compute_scores(trends: list[StandardTrend]) -> None:
    """Assign a preliminary ``score`` (0-100) to each trend in place."""
    if not trends:
        return

    # Log-scale popularity, then normalize to the batch maximum.
    log_pops = [math.log10(1 + max(t.popularity_score, 0.0)) for t in trends]
    max_log = max(log_pops) or 1.0

    max_cluster = max((t.cluster_size for t in trends), default=1) or 1

    for trend, log_pop in zip(trends, log_pops):
        freshness = _freshness(trend.published_time)
        popularity = log_pop / max_log
        corroboration = (
            math.log10(1 + trend.cluster_size) / math.log10(1 + max_cluster)
            if max_cluster > 1
            else 0.0
        )
        score = (
            W_FRESHNESS * freshness
            + W_POPULARITY * popularity
            + W_CORROBORATION * corroboration
        )
        trend.score = round(score * 100, 1)
