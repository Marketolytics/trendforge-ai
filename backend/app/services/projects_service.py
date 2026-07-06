"""Projects/history: generated content grouped into reopenable projects."""

from __future__ import annotations

from datetime import datetime, timezone

from sqlmodel import Session, select

from app.db.models import GeneratedContent, Trend
from app.db.session import engine


def _iso(dt: datetime | None) -> str | None:
    if dt is None:
        return None
    return (dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)).isoformat()


def list_projects(
    q: str | None = None,
    sort: str = "recent",  # recent | modules | title
) -> list[dict]:
    """Group generated_content by (trend_id, variant) into projects."""
    with Session(engine) as session:
        rows = list(session.exec(select(GeneratedContent)).all())
        trend_titles = {
            t.id: t.title for t in session.exec(select(Trend)).all()
        }

    groups: dict[tuple[int | None, str], dict] = {}
    for row in rows:
        key = (row.trend_id, row.variant)
        g = groups.setdefault(
            key,
            {
                "trend_id": row.trend_id,
                "variant": row.variant,
                "title": trend_titles.get(row.trend_id, row.title),
                "modules": [],
                "updated_at": None,
                "total_generation_ms": 0,
            },
        )
        g["modules"].append(row.kind)
        g["total_generation_ms"] += row.generation_ms or 0
        created = _iso(row.created_at)
        if created and (g["updated_at"] is None or created > g["updated_at"]):
            g["updated_at"] = created

    projects = list(groups.values())
    for p in projects:
        p["module_count"] = len(p["modules"])

    if q:
        needle = q.lower()
        projects = [p for p in projects if needle in (p["title"] or "").lower()]

    if sort == "modules":
        projects.sort(key=lambda p: p["module_count"], reverse=True)
    elif sort == "title":
        projects.sort(key=lambda p: (p["title"] or "").lower())
    else:  # recent
        projects.sort(key=lambda p: p["updated_at"] or "", reverse=True)

    return projects
