"""Backup, restore and project import/export — prevents data loss."""

from __future__ import annotations

import io
import json
import zipfile
from datetime import UTC, datetime, timezone  # noqa: F401  (datetime used in import_project)
from pathlib import Path

from sqlmodel import Session, select

from app.config import settings
from app.core.logging import get_logger
from app.db.models import GeneratedContent, ResearchPackage, Trend, utcnow
from app.db.session import engine

log = get_logger("trendforge.backup")

DB_ARCNAME = "trendforge.db"
MANIFEST = "manifest.json"


def _manifest(kind: str) -> dict:
    return {
        "app": settings.app_name,
        "version": settings.version,
        "kind": kind,
        "created_at": datetime.now(UTC).isoformat(),
    }


def create_backup() -> tuple[str, bytes]:
    """Zip the SQLite database with a manifest."""
    db_path = settings.resolved_database_path
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr(MANIFEST, json.dumps(_manifest("full"), indent=2))
        if db_path.exists():
            zf.writestr(DB_ARCNAME, db_path.read_bytes())
    stamp = datetime.now(UTC).strftime("%Y%m%d-%H%M%S")
    return f"trendforge-backup-{stamp}.zip", buffer.getvalue()


def write_auto_backup(retain: int = 5) -> Path | None:
    """Write a backup into the local backups directory, pruning old ones."""
    backups = settings.data_path / "backups"
    backups.mkdir(parents=True, exist_ok=True)
    name, data = create_backup()
    path = backups / name
    path.write_bytes(data)
    existing = sorted(backups.glob("trendforge-backup-*.zip"))
    for old in existing[:-retain]:
        old.unlink(missing_ok=True)
    log.info("auto backup written", extra={"category": "general", "file": name})
    return path


def restore_backup(zip_bytes: bytes) -> dict:
    """Restore the database from a backup zip. Restart recommended after."""
    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as zf:
        names = zf.namelist()
        if DB_ARCNAME not in names:
            raise ValueError("Backup does not contain a database file")
        db_bytes = zf.read(DB_ARCNAME)

    db_path = settings.resolved_database_path
    # Safety copy of the current DB before overwriting.
    if db_path.exists():
        db_path.with_suffix(".pre-restore.db").write_bytes(db_path.read_bytes())
    engine.dispose()
    db_path.write_bytes(db_bytes)
    log.info("database restored from backup", extra={"category": "general"})
    return {"ok": True, "restart_recommended": True}


def export_project(trend_id: int) -> dict | None:
    """Bundle a trend, its generated content and research into JSON."""
    with Session(engine) as s:
        trend = s.get(Trend, trend_id)
        if trend is None:
            return None
        content = [
            {"kind": g.kind, "variant": g.variant, "payload": g.payload, "params": g.params,
             "prompt_version": g.prompt_version}
            for g in s.exec(
                select(GeneratedContent).where(GeneratedContent.trend_id == trend_id)
            ).all()
        ]
        research = s.exec(
            select(ResearchPackage).where(ResearchPackage.trend_id == trend_id)
        ).first()
        return {
            **_manifest("project"),
            "trend": trend.model_dump(mode="json"),
            "content": content,
            "research": research.base if research else None,
        }


def import_project(bundle: dict) -> int:
    """Insert a project bundle as a new trend + content + research."""
    trend_data = dict(bundle.get("trend", {}))
    trend_data.pop("id", None)
    trend_data["content_hash"] = (trend_data.get("content_hash", "") + "-import")[:64] or "import"
    # Datetime fields arrive as ISO strings from JSON; let defaults handle them.
    published_raw = trend_data.pop("published_time", None)
    for dt_field in ("created_at", "collection_timestamp"):
        trend_data.pop(dt_field, None)
    with Session(engine) as s:
        trend = Trend(**{k: v for k, v in trend_data.items() if k in Trend.model_fields})
        if published_raw:
            try:
                trend.published_time = datetime.fromisoformat(published_raw)
            except (TypeError, ValueError):
                trend.published_time = None
        s.add(trend)
        s.commit()
        s.refresh(trend)
        new_id = trend.id

        for c in bundle.get("content", []):
            s.add(
                GeneratedContent(
                    trend_id=new_id,
                    title=trend.title,
                    kind=c.get("kind", "package"),
                    variant=c.get("variant", ""),
                    payload=c.get("payload", {}),
                    params=c.get("params", {}),
                    prompt_version=c.get("prompt_version", ""),
                    status="generated",
                )
            )
        if bundle.get("research"):
            s.add(
                ResearchPackage(
                    trend_id=new_id,
                    title=trend.title,
                    base=bundle["research"],
                    confidence=bundle["research"].get("research_confidence", 0),
                    source_count=len(bundle["research"].get("sources", [])),
                    updated_at=utcnow(),
                )
            )
        s.commit()
        return new_id
