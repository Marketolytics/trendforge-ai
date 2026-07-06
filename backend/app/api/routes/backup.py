"""Backup, restore and project import/export endpoints."""

from __future__ import annotations

from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import Response

from app.services import backup_service

router = APIRouter(prefix="/backup", tags=["backup"])


@router.get("")
def download_backup() -> Response:
    filename, data = backup_service.create_backup()
    return Response(
        content=data,
        media_type="application/zip",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.post("/restore")
async def restore_backup(file: UploadFile = File(...)) -> dict:
    data = await file.read()
    try:
        return backup_service.restore_backup(data)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/project/{trend_id}")
def export_project(trend_id: int) -> dict:
    bundle = backup_service.export_project(trend_id)
    if bundle is None:
        raise HTTPException(status_code=404, detail="Trend not found")
    return bundle


@router.post("/project")
def import_project(bundle: dict) -> dict:
    if bundle.get("kind") != "project" or "trend" not in bundle:
        raise HTTPException(status_code=400, detail="Not a valid project bundle")
    new_id = backup_service.import_project(bundle)
    return {"ok": True, "trend_id": new_id}
