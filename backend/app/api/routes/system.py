"""System info + optional update checking (no auto-update, no account)."""

from __future__ import annotations

import httpx
from fastapi import APIRouter

from app.config import settings
from app.core.logging import get_logger
from app.services.settings_service import SettingsService

router = APIRouter(tags=["system"])
log = get_logger("trendforge.system")


def _newer(latest: str, current: str) -> bool:
    def parts(v: str) -> tuple:
        return tuple(int(x) for x in v.strip().lstrip("v").split(".") if x.isdigit())
    try:
        return parts(latest) > parts(current)
    except Exception:  # noqa: BLE001
        return False


@router.get("/version")
def version() -> dict:
    return {"name": settings.app_name, "version": settings.version}


@router.post("/update-check")
async def update_check() -> dict:
    """Check an optional configured URL for a newer version. Never auto-updates."""
    current = settings.version
    url = (SettingsService.get("update_url") or "").strip()
    if not url:
        return {"current": current, "latest": current, "update_available": False, "checked": False}
    try:
        async with httpx.AsyncClient(timeout=8.0) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            latest = str(resp.json().get("version", current))
    except Exception as exc:  # noqa: BLE001
        log.warning("update check failed", extra={"category": "network", "error": str(exc)})
        return {"current": current, "latest": current, "update_available": False, "checked": False,
                "error": "Could not reach update server"}
    return {"current": current, "latest": latest, "update_available": _newer(latest, current), "checked": True}
