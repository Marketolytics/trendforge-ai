"""SQLite engine and session management via SQLModel."""

from __future__ import annotations

from collections.abc import Generator

from sqlmodel import Session, SQLModel, create_engine

from app.config import settings

# check_same_thread=False lets the connection be shared across FastAPI's
# threadpool for synchronous endpoints. Safe for local single-user usage.
_connect_args = {"check_same_thread": False}

engine = create_engine(
    settings.database_url,
    echo=False,
    connect_args=_connect_args,
)


def init_db() -> None:
    """Create database tables for all imported SQLModel models."""
    # Import models so they register with SQLModel.metadata before create_all.
    from app.db import models  # noqa: F401

    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
    """FastAPI dependency that yields a database session."""
    with Session(engine) as session:
        yield session
