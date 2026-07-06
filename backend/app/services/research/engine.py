"""Deterministic research engine.

Given a seed trend it assembles the *story*: related items across sources,
each scored for confidence, then builds a timeline, keyword intelligence,
entities and a small research graph. No AI required — this base package works
offline. The AI verification layer enriches it separately.
"""

from __future__ import annotations

from datetime import datetime, timezone
from difflib import SequenceMatcher

from sqlalchemy import or_
from sqlmodel import Session, select

from app.core.logging import get_logger
from app.db.models import ResearchPackage, Trend, utcnow
from app.db.session import engine as db_engine
from app.services.collectors.base import normalize_title
from app.services.research import entities as entity_svc
from app.services.research import keywords as keyword_svc
from app.services.research.confidence import classify

log = get_logger("trendforge.research")

SIMILARITY_THRESHOLD = 0.45
MAX_CANDIDATES = 80


def _iso(dt: datetime | None) -> str | None:
    if dt is None:
        return None
    return (dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)).isoformat()


def _candidates(session: Session, seed: Trend) -> list[Trend]:
    if not seed.keywords:
        return [seed]
    clauses = [Trend.title.ilike(f"%{kw}%") for kw in seed.keywords[:6]]
    rows = session.exec(
        select(Trend).where(or_(*clauses)).limit(MAX_CANDIDATES)
    ).all()
    if seed not in rows:
        rows = [seed, *rows]
    return list(rows)


def _member(trend: Trend) -> dict:
    tier = classify(trend.source, trend.source_type)
    return {
        "trend_id": trend.id,
        "title": trend.title,
        "summary": trend.summary,
        "source": trend.source,
        "source_type": trend.source_type,
        "url": trend.url,
        "published": _iso(trend.published_time),
        "keywords": trend.keywords or [],
        "tier": tier.key,
        "tier_label": tier.label,
        "score": tier.score,
        "_published_dt": trend.published_time,
    }


def build_base(trend_id: int) -> dict | None:
    with Session(db_engine) as session:
        seed = session.get(Trend, trend_id)
        if seed is None:
            return None
        seed_norm = normalize_title(seed.title)
        seed_kw = set(seed.keywords or [])

        members: list[dict] = []
        for cand in _candidates(session, seed):
            if cand.id == seed.id:
                include = True
            else:
                sim = SequenceMatcher(None, seed_norm, normalize_title(cand.title)).ratio()
                overlap = len(seed_kw & set(cand.keywords or []))
                include = sim >= SIMILARITY_THRESHOLD or overlap >= 2
            if include:
                members.append(_member(cand))

        # Related (adjacent) stories for graph navigation — share a keyword but
        # are not part of this cluster.
        member_ids = {m["trend_id"] for m in members}
        related = []
        if seed_kw:
            clauses = [Trend.title.ilike(f"%{kw}%") for kw in list(seed_kw)[:5]]
            for r in session.exec(
                select(Trend).where(or_(*clauses)).order_by(Trend.score.desc()).limit(30)
            ).all():
                if r.id not in member_ids and len(related) < 6:
                    related.append({"id": r.id, "title": r.title, "source": r.source})

        seed_title = seed.title

    # --- derived data ----------------------------------------------------
    # Sources (deduped by name).
    sources: dict[str, dict] = {}
    for m in members:
        s = sources.setdefault(
            m["source"],
            {"source": m["source"], "source_type": m["source_type"], "tier": m["tier"],
             "tier_label": m["tier_label"], "score": m["score"], "count": 0, "latest": None},
        )
        s["count"] += 1
        if m["published"] and (s["latest"] is None or m["published"] > s["latest"]):
            s["latest"] = m["published"]

    # Timeline (chronological).
    timeline = sorted(
        ({"time": m["published"], "source": m["source"], "title": m["title"], "tier": m["tier"]}
         for m in members if m["published"]),
        key=lambda e: e["time"],
    )

    kw = keyword_svc.compute(members)
    ents = entity_svc.extract(members)

    # Research confidence: member quality + breadth of coverage.
    scores = [m["score"] for m in members] or [25]
    distinct_tiers = len({m["tier"] for m in members})
    coverage = min(100, distinct_tiers * 20 + len(sources) * 3)
    research_confidence = round(0.6 * (sum(scores) / len(scores)) + 0.4 * coverage, 1)

    # Small research graph.
    nodes = [{"id": f"story:{trend_id}", "label": seed_title[:60], "type": "story"}]
    edges = []
    for c in ents["companies"][:5] + ents["platforms"][:5]:
        nid = f"entity:{c}"
        nodes.append({"id": nid, "label": c, "type": "entity"})
        edges.append({"from": f"story:{trend_id}", "to": nid})
    for r in related:
        nid = f"story:{r['id']}"
        nodes.append({"id": nid, "label": r["title"][:50], "type": "related"})
        edges.append({"from": f"story:{trend_id}", "to": nid})

    # Strip helper datetimes before persisting.
    for m in members:
        m.pop("_published_dt", None)

    base = {
        "seed_trend_id": trend_id,
        "title": seed_title,
        "member_count": len(members),
        "members": members,
        "sources": sorted(sources.values(), key=lambda s: s["score"], reverse=True),
        "timeline": timeline,
        "keywords": kw,
        "entities": ents,
        "related_stories": related,
        "graph": {"nodes": nodes, "edges": edges},
        "research_confidence": research_confidence,
        "built_at": _iso(utcnow()),
    }

    _persist(trend_id, seed_title, base, research_confidence, len(sources))
    log.info(
        "research base built",
        extra={"category": "general", "trend_id": trend_id, "members": len(members),
               "sources": len(sources), "confidence": research_confidence},
    )
    return base


def _persist(trend_id: int, title: str, base: dict, confidence: float, source_count: int) -> None:
    with Session(db_engine) as session:
        row = session.exec(
            select(ResearchPackage).where(ResearchPackage.trend_id == trend_id)
        ).first()
        if row is None:
            row = ResearchPackage(trend_id=trend_id, title=title)
        row.title = title
        row.base = base
        row.confidence = confidence
        row.source_count = source_count
        row.updated_at = utcnow()
        session.add(row)
        session.commit()


def get_base(trend_id: int, rebuild: bool = False) -> dict | None:
    if not rebuild:
        with Session(db_engine) as session:
            row = session.exec(
                select(ResearchPackage).where(ResearchPackage.trend_id == trend_id)
            ).first()
            if row is not None and row.base:
                return row.base
    return build_base(trend_id)


def list_packages() -> list[dict]:
    with Session(db_engine) as session:
        rows = session.exec(
            select(ResearchPackage).order_by(ResearchPackage.updated_at.desc())
        ).all()
        return [
            {"trend_id": r.trend_id, "title": r.title, "confidence": r.confidence,
             "source_count": r.source_count, "updated_at": _iso(r.updated_at)}
            for r in rows
        ]
