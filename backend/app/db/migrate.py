"""Lightweight, non-destructive SQLite migrations.

On startup we compare each model's columns against the live table and ADD any
that are missing. SQLite can only add nullable columns (optionally with a
literal default), which is exactly what our additive schema changes need — no
data is lost and fresh installs are unaffected.
"""

from __future__ import annotations

from sqlalchemy import inspect, text
from sqlmodel import SQLModel

from app.core.logging import get_logger
from app.db.session import engine

log = get_logger("trendforge.migrate")


def _sqlite_default(column) -> str:
    """Return a ' DEFAULT <literal>' clause for simple defaults, else ''."""
    default = getattr(column, "default", None)
    if default is None or getattr(default, "is_callable", False):
        return ""
    arg = getattr(default, "arg", None)
    if callable(arg) or arg is None:
        return ""
    if isinstance(arg, bool):
        return f" DEFAULT {1 if arg else 0}"
    if isinstance(arg, (int, float)):
        return f" DEFAULT {arg}"
    if isinstance(arg, str):
        escaped = arg.replace("'", "''")
        return f" DEFAULT '{escaped}'"
    return ""


def run_migrations() -> None:
    """Add any model columns missing from existing tables."""
    inspector = inspect(engine)
    added = 0
    with engine.begin() as conn:
        for table in SQLModel.metadata.sorted_tables:
            if not inspector.has_table(table.name):
                continue
            existing = {c["name"] for c in inspector.get_columns(table.name)}
            for column in table.columns:
                if column.name in existing:
                    continue
                col_type = column.type.compile(dialect=engine.dialect)
                # JSON columns need a sensible default so ORM reads don't choke.
                default_clause = _sqlite_default(column)
                if not default_clause and col_type.upper() in {"JSON", "TEXT"}:
                    default_clause = " DEFAULT '{}'" if col_type.upper() == "JSON" else ""
                ddl = (
                    f'ALTER TABLE "{table.name}" '
                    f'ADD COLUMN "{column.name}" {col_type}{default_clause}'
                )
                conn.execute(text(ddl))
                added += 1
                log.info(
                    "migration: added column",
                    extra={"category": "general", "table": table.name, "column": column.name},
                )
    if added:
        log.info("migrations applied", extra={"category": "general", "columns_added": added})
