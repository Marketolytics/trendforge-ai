"""Lightweight, non-destructive additive migrations (SQLite + MySQL).

On startup we compare each model's columns against the live table and ADD any
that are missing. Both SQLite and MySQL support ``ALTER TABLE ADD COLUMN`` for
nullable columns, which is exactly what our additive schema changes need — no
data is lost and fresh installs (created via ``create_all``) are unaffected.

Identifier quoting and column types are resolved through the active dialect, so
the same logic works across databases.
"""

from __future__ import annotations

from sqlalchemy import inspect, text

from app.core.logging import get_logger
from app.db.session import engine

log = get_logger("trendforge.migrate")


def _literal_default(column, is_sqlite: bool) -> str:
    """Return a ' DEFAULT <literal>' clause for simple scalar defaults."""
    default = getattr(column, "default", None)
    if default is None or getattr(default, "is_callable", False):
        # No literal default; for JSON/TEXT give SQLite a sane default so ORM
        # reads don't choke. MySQL adds the column as NULLable which is fine.
        if is_sqlite:
            col_type = column.type.compile(dialect=engine.dialect).upper()
            if col_type == "JSON":
                return " DEFAULT '{}'"
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
    """Add any model columns missing from existing tables (idempotent)."""
    # Import models so they register with SQLModel.metadata.
    from sqlmodel import SQLModel

    from app.db import models  # noqa: F401

    inspector = inspect(engine)
    preparer = engine.dialect.identifier_preparer
    is_sqlite = engine.dialect.name == "sqlite"
    added = 0

    for table in SQLModel.metadata.sorted_tables:
        if not inspector.has_table(table.name):
            continue
        existing = {c["name"] for c in inspector.get_columns(table.name)}
        for column in table.columns:
            if column.name in existing:
                continue
            col_type = column.type.compile(dialect=engine.dialect)
            default_clause = _literal_default(column, is_sqlite)
            ddl = (
                f"ALTER TABLE {preparer.quote(table.name)} "
                f"ADD COLUMN {preparer.quote(column.name)} {col_type}{default_clause}"
            )
            try:
                with engine.begin() as conn:
                    conn.execute(text(ddl))
                added += 1
                log.info(
                    "migration: added column",
                    extra={"category": "general", "table": table.name, "column": column.name},
                )
            except Exception as exc:  # noqa: BLE001 - never abort startup on one column
                log.warning(
                    "migration: could not add column",
                    extra={
                        "category": "error",
                        "table": table.name,
                        "column": column.name,
                        "error": str(exc),
                    },
                )
    if added:
        log.info("migrations applied", extra={"category": "general", "columns_added": added})
