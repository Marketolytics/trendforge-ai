"""TrendForge AI - FastAPI application entrypoint."""

from __future__ import annotations

from contextlib import asynccontextmanager
from datetime import UTC

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.router import api_router
from app.config import settings
from app.core.logging import configure_logging, get_logger
from app.db.migrate import run_migrations
from app.db.seed import seed_sources
from app.db.session import init_db
from app.services.settings_service import SettingsService


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize resources on startup."""
    settings.ensure_dirs()
    configure_logging()
    init_db()
    run_migrations()
    SettingsService.seed_defaults()
    seed_sources()

    # Migrate any legacy plaintext Gemini key into the OS credential store.
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

    # Start the orchestrator worker and resume any interrupted jobs.
    from app.services.orchestrator import engine as orchestrator

    orchestrator.start_worker()
    orchestrator.resume_pending()

    # First-run marker (workspace/db/migrations above are idempotent every start).
    if SettingsService.get("initialized_at") is None:
        from datetime import datetime

        SettingsService.set("initialized_at", datetime.now(UTC).isoformat())
        get_logger("trendforge").info(
            "first-run initialization complete", extra={"category": "general"}
        )

    # Optional automatic backup on startup.
    if SettingsService.all(mask_secrets=False).get("auto_backup"):
        try:
            from app.services.backup_service import write_auto_backup

            write_auto_backup()
        except Exception:  # noqa: BLE001
            pass

    get_logger("trendforge").info(
        "TrendForge backend ready",
        extra={"category": "general", "version": settings.version},
    )
    yield


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        version=settings.version,
        lifespan=lifespan,
    )

    # Local-only single-user app: the backend is bound to 127.0.0.1 and uses no
    # cookie credentials, so allow any local origin. This covers the Tauri
    # webview origin (http://tauri.localhost on Windows), the Vite dev server,
    # and any auto-selected port — avoiding origin/CORS surprises.
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )

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
