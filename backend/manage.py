"""TrendForge AI management CLI.

Database and maintenance tasks for local development and Hostinger deployment.
All commands are safe to re-run (idempotent) and never drop existing data.

Usage:
    python manage.py initdb       # create tables + seed defaults (first deploy)
    python manage.py migrate      # apply additive column migrations
    python manage.py seed         # (re)seed default trend sources if empty
    python manage.py check        # verify DB connectivity + report config
    python manage.py backup [path]        # write a database backup zip
    python manage.py restore <path>       # restore the database from a backup zip
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


def _cmd_initdb() -> int:
    from app.config import settings
    from app.core.logging import configure_logging
    from app.db.migrate import run_migrations
    from app.db.seed import seed_sources
    from app.db.session import init_db
    from app.services.settings_service import SettingsService

    settings.ensure_dirs()
    configure_logging()
    init_db()
    run_migrations()
    SettingsService.seed_defaults()
    seed_sources()
    print(f"Database ready at: {settings.database_url}")
    return 0


def _cmd_migrate() -> int:
    from app.core.logging import configure_logging
    from app.db.migrate import run_migrations
    from app.db.session import init_db

    configure_logging()
    init_db()          # create any brand-new tables
    run_migrations()   # add any missing columns
    print("Migrations complete.")
    return 0


def _cmd_seed() -> int:
    from app.core.logging import configure_logging
    from app.db.seed import seed_sources
    from app.services.settings_service import SettingsService

    configure_logging()
    SettingsService.seed_defaults()
    seed_sources()
    print("Seed complete.")
    return 0


def _cmd_check() -> int:
    from sqlalchemy import text

    from app.config import settings
    from app.db.session import engine

    print(f"APP_ENV      : {settings.app_env}")
    print(f"DATABASE_URL : {_mask_url(settings.database_url)}")
    print(f"DATA_DIR     : {settings.data_dir}")
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("Database     : OK (connected)")
        return 0
    except Exception as exc:  # noqa: BLE001
        print(f"Database     : FAILED ({exc})")
        return 1


def _cmd_backup(dest: str | None) -> int:
    from app.services.backup_service import create_backup

    name, data = create_backup()
    out = Path(dest) if dest else Path(name)
    if out.is_dir():
        out = out / name
    out.write_bytes(data)
    print(f"Backup written: {out} ({len(data)} bytes)")
    return 0


def _cmd_restore(path: str) -> int:
    from app.services.backup_service import restore_backup

    src = Path(path)
    if not src.is_file():
        print(f"Backup file not found: {src}")
        return 1
    result = restore_backup(src.read_bytes())
    print(f"Restore complete: {result}")
    return 0


def _mask_url(url: str) -> str:
    """Hide credentials in a database URL for display."""
    if "@" in url and "//" in url:
        scheme, rest = url.split("//", 1)
        creds, host = rest.split("@", 1)
        user = creds.split(":", 1)[0]
        return f"{scheme}//{user}:***@{host}"
    return url


def main(argv: list[str] | None = None) -> int:
    # Make the backend package importable when run from any directory.
    base = Path(__file__).resolve().parent
    if str(base) not in sys.path:
        sys.path.insert(0, str(base))

    parser = argparse.ArgumentParser(description="TrendForge AI management CLI")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("initdb", help="Create tables and seed defaults")
    sub.add_parser("migrate", help="Apply additive migrations")
    sub.add_parser("seed", help="Seed default sources/settings if empty")
    sub.add_parser("check", help="Verify database connectivity and config")
    p_backup = sub.add_parser("backup", help="Write a database backup zip")
    p_backup.add_argument("dest", nargs="?", default=None, help="Output file or directory")
    p_restore = sub.add_parser("restore", help="Restore the database from a backup zip")
    p_restore.add_argument("path", help="Path to a backup zip")

    args = parser.parse_args(argv)

    if args.command == "initdb":
        return _cmd_initdb()
    if args.command == "migrate":
        return _cmd_migrate()
    if args.command == "seed":
        return _cmd_seed()
    if args.command == "check":
        return _cmd_check()
    if args.command == "backup":
        return _cmd_backup(args.dest)
    if args.command == "restore":
        return _cmd_restore(args.path)
    parser.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
