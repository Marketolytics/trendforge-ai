"""Backup + project export/import."""

from __future__ import annotations

import io
import zipfile

from sqlmodel import Session

from app.db.models import GeneratedContent, Trend
from app.db.session import engine
from app.services import backup_service


def test_create_backup_contains_db_and_manifest():
    filename, data = backup_service.create_backup()
    assert filename.endswith(".zip")
    with zipfile.ZipFile(io.BytesIO(data)) as zf:
        names = zf.namelist()
        assert "manifest.json" in names
        assert "trendforge.db" in names


def test_project_export_import_roundtrip():
    with Session(engine) as s:
        trend = Trend(title="Backup Trend", source="unit", content_hash="backup-hash", score=10)
        s.add(trend)
        s.commit()
        s.refresh(trend)
        tid = trend.id
        s.add(GeneratedContent(trend_id=tid, title="Backup Trend", kind="script",
                               payload={"data": {"hook": "hi"}}))
        s.commit()

    bundle = backup_service.export_project(tid)
    assert bundle is not None
    assert bundle["kind"] == "project"
    assert len(bundle["content"]) == 1

    new_id = backup_service.import_project(bundle)
    assert new_id != tid
    with Session(engine) as s:
        assert s.get(Trend, new_id) is not None
