"""Database insert/query round-trip."""

from __future__ import annotations

from sqlmodel import Session, select

from app.db.models import Trend
from app.db.session import engine


def test_trend_crud():
    with Session(engine) as s:
        trend = Trend(title="Test Trend", source="unit", content_hash="unit-hash", score=42.0)
        s.add(trend)
        s.commit()
        s.refresh(trend)
        tid = trend.id

    with Session(engine) as s:
        loaded = s.get(Trend, tid)
        assert loaded is not None
        assert loaded.title == "Test Trend"
        found = s.exec(select(Trend).where(Trend.source == "unit")).first()
        assert found is not None
