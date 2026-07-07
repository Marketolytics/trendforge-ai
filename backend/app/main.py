"""TrendForge AI - FastAPI application entrypoint.

Runs identically under a local ASGI server (uvicorn) and under Hostinger's
Passenger (WSGI) via ``passenger_wsgi.py``. Because WSGI has no lifespan
protocol, startup work is factored into :func:`initialize`, which is idempotent
and invoked from both the ASGI lifespan and the WSGI entrypoint.
"""

from __future__ import annotations

from contextlib import asynccontextmanager
from datetime import UTC

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from app.api.router import api_router
from app.config import settings
from app.core.logging import configure_logging, get_logger

_INITIALIZED = False


def initialize() -> None:
    """Idempotent application startup: dirs, logging, DB, seed, worker."""
    global _INITIALIZED
    if _INITIALIZED:
        return

    from app.db.migrate import run_migrations
    from app.db.seed import seed_sources
    from app.db.session import init_db
    from app.services.settings_service import SettingsService

    settings.ensure_dirs()
    configure_logging()

    # Schema + seed. Wrapped so concurrent serverless cold starts racing on
    # create_all/seed never fail a request (all operations are idempotent).
    try:
        init_db()
        run_migrations()
        SettingsService.seed_defaults()
        seed_sources()
    except Exception:  # noqa: BLE001
        get_logger("trendforge").warning(
            "database initialization encountered an error (continuing)",
            extra={"category": "error"},
        )

    # Migrate any legacy plaintext Gemini key into the credential store.
    try:
        from sqlmodel import Session

        from app.db.models import Setting
        from app.db.session import engine as _engine
        from app.services.ai import credentials as _cred

        with Session(_engine) as _s:
            legacy = _s.get(Setting, "gemini_api_key")
            if legacy and legacy.value:
                _cred.set_key("gemini", legacy.value)
                _s.delete(legacy)
                _s.commit()
                get_logger("trendforge").info(
                    "migrated legacy API key to credential store",
                    extra={"category": "general"},
                )
    except Exception:  # noqa: BLE001
        pass

    # Start the orchestrator worker and resume any interrupted jobs. Skipped on
    # serverless: there is no persistent event loop across invocations, so the
    # background queue can't run. Direct AI endpoints still work per request.
    if not settings.is_serverless:
        try:
            from app.services.orchestrator import engine as orchestrator

            orchestrator.start_worker()
            orchestrator.resume_pending()
        except Exception:  # noqa: BLE001 - never block startup on the worker
            get_logger("trendforge").warning(
                "orchestrator worker could not start", extra={"category": "error"}
            )

    # First-run marker (all steps above are idempotent every start).
    if SettingsService.get("initialized_at") is None:
        from datetime import datetime

        SettingsService.set("initialized_at", datetime.now(UTC).isoformat())
        get_logger("trendforge").info(
            "first-run initialization complete", extra={"category": "general"}
        )

    # Optional automatic backup on startup (SQLite only).
    if settings.is_sqlite and SettingsService.all(mask_secrets=False).get("auto_backup"):
        try:
            from app.services.backup_service import write_auto_backup

            write_auto_backup()
        except Exception:  # noqa: BLE001
            pass

    get_logger("trendforge").info(
        "TrendForge backend ready",
        extra={"category": "general", "version": settings.version, "env": settings.app_env},
    )
    _INITIALIZED = True


@asynccontextmanager
async def lifespan(app: FastAPI):
    """ASGI lifespan hook (uvicorn) — delegates to the shared initializer."""
    initialize()
    yield


def _add_security_headers(app: FastAPI) -> None:
    @app.middleware("http")
    async def security_headers(request: Request, call_next):  # noqa: ANN202
        response = await call_next(request)
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "SAMEORIGIN")
        response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
        response.headers.setdefault("X-XSS-Protection", "0")
        if settings.is_production:
            response.headers.setdefault(
                "Strict-Transport-Security", "max-age=31536000; includeSubDomains"
            )
        return response


def _mount_frontend(app: FastAPI) -> bool:
    """Serve the built React app (with SPA fallback) if it's co-hosted."""
    dist = settings.resolved_frontend_dist
    index = dist / "index.html"
    if not index.exists():
        return False

    assets = dist / "assets"
    if assets.is_dir():
        app.mount("/assets", StaticFiles(directory=str(assets)), name="assets")

    reserved = ("api/", "api", "docs", "redoc", "openapi.json")

    @app.get("/{full_path:path}", include_in_schema=False)
    async def spa(full_path: str):  # noqa: ANN202
        # Never shadow the API or docs endpoints.
        if full_path.startswith(reserved):
            raise HTTPException(status_code=404, detail="Not Found")
        candidate = dist / full_path
        if full_path and candidate.is_file():
            return FileResponse(candidate)
        # Fallback to index.html so client-side routes survive a refresh.
        return FileResponse(index)

    return True


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        version=settings.version,
        lifespan=lifespan,
    )

    # Compress large responses (JSON payloads, exports).
    app.add_middleware(GZipMiddleware, minimum_size=1000)

    # CORS: in development Vite proxies /api (same-origin). When the frontend is
    # served from a different origin, allow the configured origins.
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list or ["*"],
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    _add_security_headers(app)

    app.include_router(api_router)

    @app.exception_handler(Exception)
    async def _unhandled(request: Request, exc: Exception):  # noqa: ANN202
        get_logger("trendforge.error").error(
            "unhandled request error",
            extra={"category": "error", "path": str(request.url.path), "error": str(exc)},
        )
        return JSONResponse(
            status_code=500,
            content={"detail": "An unexpected error occurred. Please try again."},
        )

    # Serve the built frontend when present; otherwise expose a small JSON root.
    frontend_served = _mount_frontend(app)
    if not frontend_served:

        @app.get("/")
        def root() -> dict[str, str]:
            return {"app": settings.app_name, "docs": "/docs", "health": "/api/health"}

    return app


app = create_app()


def main() -> None:
    """Run the development server (python -m app.main)."""
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=True,
    )


if __name__ == "__main__":
    main()
