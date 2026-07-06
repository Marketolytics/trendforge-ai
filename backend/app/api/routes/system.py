"""System info + optional update checking (no auto-update, no account)."""

from __future__ import annotations

import httpx
from fastapi import APIRouter
from sqlalchemy import text

from app.config import settings
from app.core.logging import get_logger
from app.db.session import engine
from app.services.settings_service import SettingsService

router = APIRouter(tags=["system"])
log = get_logger("trendforge.system")


def _check_database() -> tuple[bool, str | None]:
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True, None
    except Exception as exc:  # noqa: BLE001
        return False, str(exc)


def _check_workspace() -> tuple[bool, list[str]]:
    missing = [name for name, path in settings.workspace_dirs.items() if not path.exists()]
    return (len(missing) == 0), missing


@router.get("/system/health-report")
def health_report() -> dict:
    from app.services.ai import router as model_router
    from app.services.ai.service import ai_service
    from app.services.cache import cache

    db_ok, db_err = _check_database()
    ws_ok, ws_missing = _check_workspace()
    try:
        cache.stats()
        cache_ok = True
    except Exception:  # noqa: BLE001
        cache_ok = False

    configured = ai_service.is_configured
    issues: list[str] = []
    if not db_ok:
        issues.append(f"Database: {db_err}")
    if not ws_ok:
        issues.append(f"Missing workspace folders: {', '.join(ws_missing)}")
    if not cache_ok:
        issues.append("Cache unavailable")
    if not configured:
        issues.append("No AI provider configured")

    return {
        "backend": "ok",
        "database": "ok" if db_ok else "error",
        "cache": "ok" if cache_ok else "error",
        "workspace": "ok" if ws_ok else "incomplete",
        "ai_provider": {"configured": configured, "provider": model_router.current_provider()},
        "network": "unknown",  # optional; not probed by default
        "first_run": SettingsService.get("initialized_at") is None,
        "issues": issues,
        "healthy": not issues or (db_ok and ws_ok and cache_ok),
    }


@router.get("/system/diagnostics")
def diagnostics() -> dict:
    from app.services.ai import router as model_router
    from app.services.ai.service import ai_service
    from app.services.cache import cache
    from app.services.orchestrator import engine as orchestrator

    queue = orchestrator.queue_stats()
    return {
        "version": settings.version,
        "backend_port": settings.port,
        "workspace": {name: str(path) for name, path in settings.workspace_dirs.items()},
        "database_path": str(settings.resolved_database_path),
        "log_dir": str(settings.resolved_log_dir),
        "ai_provider": {
            "provider": model_router.current_provider(),
            "configured": ai_service.is_configured,
            "models": {
                "research": model_router.model_for("research"),
                "content": model_router.model_for("content"),
                "quality": model_router.model_for("quality"),
            },
        },
        "cache": cache.stats(),
        "queue": queue,
        "running_jobs": queue.get("by_status", {}).get("running", 0),
    }


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
