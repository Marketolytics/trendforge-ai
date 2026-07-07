"""SQLite engine and session management via SQLModel."""

from __future__ import annotations

from collections.abc import Generator

from sqlmodel import Session, SQLModel, create_engine

from app.config import settings


def _make_engine():
    """Create a SQLAlchemy engine tuned for the configured database.

    - SQLite (development): allow cross-thread use for FastAPI's threadpool.
    - Serverless (Vercel + Postgres): use NullPool — each invocation is
      short-lived and isolated, so persistent pooling wastes/leaks connections.
      Pair this with a provider-side pooler (Vercel Postgres/Neon/Supabase).
    - Long-running server (MySQL/Postgres on a VPS or shared host): pooled
      connections with pre-ping and a recycle window so idle connections don't
      go stale.
    """
    url = settings.database_url
    if url.startswith("sqlite"):
        return create_engine(
            url,
            echo=False,
            connect_args={"check_same_thread": False},
        )

    if settings.is_serverless:
        from sqlalchemy.pool import NullPool

        return create_engine(url, echo=False, poolclass=NullPool, pool_pre_ping=True)

    # Long-running networked database (MySQL via PyMySQL, Postgres via psycopg).
    return create_engine(
        url,
        echo=False,
        pool_pre_ping=True,   # transparently replace dropped connections
        pool_recycle=280,     # recycle before typical wait_timeout windows
        pool_size=5,
        max_overflow=10,
    )


engine = _make_engine()


def init_db() -> None:
    """Create database tables for all imported SQLModel models."""
    # Import models so they register with SQLModel.metadata before create_all.
    from app.db import models  # noqa: F401

    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
    """FastAPI dependency that yields a database session."""
    with Session(engine) as session:
        yield session
