"""Local analytics aggregation (no cloud sync)."""

from __future__ import annotations

from collections import Counter
from datetime import datetime, timedelta, timezone

from sqlalchemy import func
from sqlmodel import Session, select

from app.db.models import (
    CompetitorChannel,
    GeneratedContent,
    History,
    Trend,
)
from app.db.session import engine


def _as_utc(dt: datetime) -> datetime:
    return dt.replace(tzinfo=timezone.utc) if dt.tzinfo is None else dt


def compute() -> dict:
    now = datetime.now(timezone.utc)
    day_ago = now - timedelta(hours=24)
    week_ago = now - timedelta(days=7)

    with Session(engine) as session:
        total_trends = session.scalar(select(func.count()).select_from(Trend)) or 0
        trends_today = (
            session.scalar(
                select(func.count()).select_from(Trend).where(Trend.collection_timestamp >= day_ago)
            )
            or 0
        )
        ai_generations = (
            session.scalar(
                select(func.count()).select_from(History).where(History.event == "ai_generate")
            )
            or 0
        )

        trends = list(session.exec(select(Trend)).all())
        generated = list(session.exec(select(GeneratedContent)).all())
        history = list(
            session.exec(select(History).where(History.created_at >= week_ago)).all()
        )
        competitors = session.scalar(select(func.count()).select_from(CompetitorChannel)) or 0

    # Category distribution.
    category_counts = Counter(t.category for t in trends)
    top_categories = [
        {"category": c, "count": n} for c, n in category_counts.most_common(6)
    ]

    # Top opportunities (preliminary score, or AI opportunity when analyzed).
    top_opportunities = sorted(trends, key=lambda t: t.score, reverse=True)[:5]

    # Generations by module kind.
    kind_counts = Counter(g.kind for g in generated)
    generations_by_kind = [
        {"kind": k, "count": n} for k, n in kind_counts.most_common()
    ]

    # Most used hook types (from generated hooks payloads).
    hook_types: Counter = Counter()
    for g in generated:
        if g.kind == "hooks":
            for h in (g.payload or {}).get("data", {}).get("hooks", []):
                if isinstance(h, dict) and h.get("type"):
                    hook_types[h["type"]] += 1
    most_used_hooks = [{"type": t, "count": n} for t, n in hook_types.most_common(7)]

    # Weekly activity (events per day, last 7 days).
    day_buckets: Counter = Counter()
    for h in history:
        day = _as_utc(h.created_at).date().isoformat()
        day_buckets[day] += 1
    weekly_activity = []
    for i in range(6, -1, -1):
        day = (now - timedelta(days=i)).date().isoformat()
        weekly_activity.append({"day": day, "count": day_buckets.get(day, 0)})

    return {
        "trends_today": int(trends_today),
        "total_trends": int(total_trends),
        "ai_generations": int(ai_generations),
        "competitors": int(competitors),
        "content_packages": len({(g.trend_id, g.variant) for g in generated}),
        "top_categories": top_categories,
        "generations_by_kind": generations_by_kind,
        "most_used_hooks": most_used_hooks,
        "weekly_activity": weekly_activity,
        "top_opportunities": [
            {"id": t.id, "title": t.title, "score": t.score, "source": t.source}
            for t in top_opportunities
        ],
    }
