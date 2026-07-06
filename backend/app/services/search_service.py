"""Global search across trends, projects, favorites, research and content."""

from __future__ import annotations

from sqlmodel import Session, select

from app.db.models import (
    Favorite,
    GeneratedContent,
    ResearchPackage,
    Trend,
)
from app.db.session import engine


def search(q: str, per_type: int = 6) -> list[dict]:
    """Return a flat, ranked list of matches across the app."""
    q = (q or "").strip()
    if not q:
        return []
    like = f"%{q}%"
    results: list[dict] = []

    with Session(engine) as s:
        for t in s.exec(select(Trend).where(Trend.title.ilike(like)).order_by(Trend.score.desc()).limit(per_type)).all():
            results.append({"type": "trend", "id": t.id, "title": t.title, "subtitle": t.source})

        for r in s.exec(
            select(ResearchPackage).where(ResearchPackage.title.ilike(like)).limit(per_type)
        ).all():
            results.append({"type": "research", "id": r.trend_id, "title": r.title, "subtitle": "research"})

        for f in s.exec(select(Favorite).where(Favorite.label.ilike(like)).limit(per_type)).all():
            results.append({"type": "favorite", "id": f.id, "title": f.label, "subtitle": f.type})

        # Generated modules (scripts, hooks, storyboards, prompts…) — match the
        # owning trend title, grouped by kind.
        seen: set[tuple] = set()
        for g in s.exec(
            select(GeneratedContent).where(GeneratedContent.title.ilike(like)).limit(per_type * 3)
        ).all():
            key = (g.trend_id, g.kind)
            if key in seen:
                continue
            seen.add(key)
            results.append(
                {"type": "content", "id": g.trend_id, "title": g.title, "subtitle": g.kind, "variant": g.variant}
            )
            if len([r for r in results if r["type"] == "content"]) >= per_type:
                break

    return results
