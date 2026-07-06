"""Research engine: confidence, keywords, entities, base build."""

from __future__ import annotations

from sqlmodel import Session

from app.db.models import Trend
from app.db.session import engine
from app.services.research import engine as research_engine
from app.services.research import entities, keywords
from app.services.research.confidence import classify


def test_confidence_tiers():
    assert classify("Steam · CS2", "steam").key == "official"
    assert classify("IGN", "gaming_news").key == "industry"
    assert classify("r/gaming", "reddit").key == "community"
    assert classify("YouTube", "youtube").key == "social"


def test_entities_no_substring_false_positive():
    # "real" must not trigger the "ea" company match.
    result = entities.extract([{"title": "This is all about real control", "keywords": []}])
    assert "Ea" not in result["companies"]


def test_keywords_compute():
    members = [
        {"title": "GTA 6 trailer breakdown", "summary": "", "keywords": ["gta", "trailer"]},
        {"title": "GTA 6 map details revealed", "summary": "", "keywords": ["gta", "map"]},
    ]
    kw = keywords.compute(members)
    words = {k["word"] for k in kw["trending"]}
    assert "gta" in words


def test_build_base_clusters_related():
    with Session(engine) as s:
        seed = Trend(title="Halo Infinite Season 8 announced", source="IGN",
                     source_type="gaming_news", content_hash="h-seed",
                     keywords=["halo", "infinite", "season"], score=80)
        related = Trend(title="Halo Infinite Season 8 brings new maps", source="r/halo",
                        source_type="reddit", content_hash="h-rel",
                        keywords=["halo", "infinite", "maps"], score=40)
        s.add(seed)
        s.add(related)
        s.commit()
        s.refresh(seed)
        seed_id = seed.id

    base = research_engine.build_base(seed_id)
    assert base is not None
    assert base["member_count"] >= 2
    assert base["research_confidence"] > 0
    assert len(base["sources"]) >= 1
