"""TrendForge AI - FastAPI application entrypoint."""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(api_router)

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
