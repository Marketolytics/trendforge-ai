"""Aggregation engine.

Runs every enabled collector concurrently, then:
  1. merges all normalized trends,
  2. removes exact duplicates (by content hash),
  3. clusters near-duplicate stories (fuzzy title match),
  4. assigns a preliminary score,
  5. upserts the result into SQLite,
  6. records the run in the history log.
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from datetime import datetime, timezone
from difflib import SequenceMatcher

from sqlmodel import Session, select

from app.core.logging import get_logger, log_refresh, performance
from app.db.models import History, Trend, TrendSource, utcnow
from app.db.session import engine
from app.services.collectors.base import StandardTrend, normalize_title
from app.services.collectors.registry import build_collector
from app.services.intelligence.preliminary import compute_scores

log = get_logger("trendforge.aggregation")

COLLECTOR_TIMEOUT = 30.0       # seconds per collector
SIMILARITY_THRESHOLD = 0.72    # fuzzy title match for clustering


@dataclass
class RefreshResult:
    trends_collected: int = 0
    raw_items: int = 0
    sources_ok: int = 0
    sources_failed: int = 0
    duration_ms: int = 0
    failures: list[dict] = field(default_factory=list)

    def as_dict(self) -> dict:
        return {
            "trends_collected": self.trends_collected,
            "raw_items": self.raw_items,
            "sources_ok": self.sources_ok,
            "sources_failed": self.sources_failed,
            "duration_ms": self.duration_ms,
            "failures": self.failures,
        }


async def _run_collector(source: TrendSource) -> list[StandardTrend]:
    collector = build_collector(source)
    if collector is None:
        raise RuntimeError(f"no collector for type '{source.type}'")
    with performance(f"collect:{source.name}", source=source.name, type=source.type):
        return await asyncio.wait_for(collector.collect(), timeout=COLLECTOR_TIMEOUT)


def _load_enabled_sources() -> list[TrendSource]:
    with Session(engine) as session:
        return list(session.exec(select(TrendSource).where(TrendSource.enabled == True)).all())  # noqa: E712


def _dedupe_and_cluster(items: list[StandardTrend]) -> list[StandardTrend]:
    """Collapse exact duplicates then cluster near-duplicate stories."""
    # Exact dedupe by content hash, keeping the strongest popularity signal.
    by_hash: dict[str, StandardTrend] = {}
    for item in items:
        existing = by_hash.get(item.content_hash)
        if existing is None or item.popularity_score > existing.popularity_score:
            if existing is not None:
                item.cluster_size = existing.cluster_size  # preserve prior merges
            by_hash[item.content_hash] = item
        else:
            existing.cluster_size += 0  # exact dupes don't inflate corroboration

    unique = list(by_hash.values())
    n = len(unique)
    norms = [normalize_title(t.title) for t in unique]

    # Keyword blocking: only titles sharing a keyword are compared, turning an
    # O(n^2) scan into a handful of comparisons per item.
    inverted: dict[str, list[int]] = {}
    for idx, trend in enumerate(unique):
        for kw in trend.keywords:
            inverted.setdefault(kw, []).append(idx)

    assigned = [False] * n
    representatives: list[StandardTrend] = []
    matcher = SequenceMatcher(autojunk=False)

    for i, trend in enumerate(unique):
        if assigned[i]:
            continue
        cluster = [i]
        assigned[i] = True

        candidates: set[int] = set()
        for kw in trend.keywords:
            candidates.update(inverted.get(kw, ()))

        matcher.set_seq2(norms[i])
        for j in candidates:
            if j <= i or assigned[j]:
                continue
            matcher.set_seq1(norms[j])
            # Cheap prefilters before the full ratio computation.
            if matcher.real_quick_ratio() < SIMILARITY_THRESHOLD:
                continue
            if matcher.quick_ratio() < SIMILARITY_THRESHOLD:
                continue
            if matcher.ratio() >= SIMILARITY_THRESHOLD:
                assigned[j] = True
                cluster.append(j)

        members = [unique[k] for k in cluster]
        rep = max(members, key=lambda t: (t.popularity_score, t.published_time or datetime.min.replace(tzinfo=timezone.utc)))
        rep.cluster_id = rep.content_hash
        rep.cluster_size = len(members)
        # Merge keywords across the cluster (unique, capped).
        merged_keywords: list[str] = []
        for member in members:
            for kw in member.keywords:
                if kw not in merged_keywords:
                    merged_keywords.append(kw)
        rep.keywords = merged_keywords[:10]
        representatives.append(rep)

    return representatives


def _persist(trends: list[StandardTrend]) -> int:
    """Upsert aggregated trends by content hash. Returns count stored."""
    now = utcnow()
    with Session(engine) as session:
        for t in trends:
            existing = session.exec(
                select(Trend).where(Trend.content_hash == t.content_hash)
            ).first()
            if existing is None:
                session.add(_to_row(t, now))
            else:
                existing.popularity_score = t.popularity_score
                existing.score = t.score
                existing.cluster_size = t.cluster_size
                existing.cluster_id = t.cluster_id
                existing.keywords = t.keywords
                existing.summary = t.summary or existing.summary
                existing.image_url = t.image_url or existing.image_url
                existing.url = t.url or existing.url
                existing.published_time = t.published_time or existing.published_time
                existing.collection_timestamp = now
                session.add(existing)
        session.commit()
    return len(trends)


def _to_row(t: StandardTrend, now: datetime) -> Trend:
    return Trend(
        title=t.title,
        summary=t.summary,
        url=t.url,
        source=t.source,
        source_type=t.source_type,
        published_time=t.published_time,
        category=t.category,
        keywords=t.keywords,
        popularity_score=t.popularity_score,
        image_url=t.image_url,
        language=t.language,
        region=t.region,
        raw_content=t.raw_content,
        collection_timestamp=now,
        source_id=t.source_id,
        content_hash=t.content_hash,
        cluster_id=t.cluster_id,
        cluster_size=t.cluster_size,
        score=t.score,
    )


def _record_history(result: RefreshResult) -> None:
    status = "success"
    if result.sources_failed and result.sources_ok:
        status = "partial"
    elif result.sources_failed and not result.sources_ok:
        status = "error"
    with Session(engine) as session:
        session.add(
            History(
                event="refresh",
                status=status,
                trends_collected=result.trends_collected,
                sources_ok=result.sources_ok,
                sources_failed=result.sources_failed,
                duration_ms=result.duration_ms,
                detail=result.as_dict(),
            )
        )
        session.commit()


async def refresh_trends(force: bool = False) -> RefreshResult:  # noqa: ARG001
    """Collect, aggregate and persist trends from all enabled sources."""
    start = asyncio.get_event_loop().time()
    result = RefreshResult()

    sources = await asyncio.to_thread(_load_enabled_sources)
    log_refresh("refresh started", sources=len(sources), force=force)

    tasks = [_run_collector(src) for src in sources]
    collected = await asyncio.gather(*tasks, return_exceptions=True)

    merged: list[StandardTrend] = []
    for src, outcome in zip(sources, collected):
        if isinstance(outcome, Exception):
            result.sources_failed += 1
            result.failures.append({"source": src.name, "error": str(outcome)})
            log.warning(
                "collector failed",
                extra={"category": "refresh", "source": src.name, "error": str(outcome)},
            )
        else:
            result.sources_ok += 1
            merged.extend(outcome)

    result.raw_items = len(merged)

    with performance("aggregate:dedupe_cluster", items=len(merged)):
        aggregated = await asyncio.to_thread(_dedupe_and_cluster, merged)
    compute_scores(aggregated)
    aggregated.sort(key=lambda t: t.score, reverse=True)

    with performance("aggregate:persist", items=len(aggregated)):
        result.trends_collected = await asyncio.to_thread(_persist, aggregated)
    result.duration_ms = int((asyncio.get_event_loop().time() - start) * 1000)

    await asyncio.to_thread(_record_history, result)
    log_refresh(
        "refresh complete",
        trends=result.trends_collected,
        raw=result.raw_items,
        ok=result.sources_ok,
        failed=result.sources_failed,
        duration_ms=result.duration_ms,
    )
    return result
