"""Test setup: isolate every run in a throwaway data directory + database."""

from __future__ import annotations

import os
import tempfile
from pathlib import Path

# Point the app at a temp data dir BEFORE any app module is imported so the
# cached settings pick it up.
_TMP = Path(tempfile.mkdtemp(prefix="trendforge_test_"))
os.environ["TRENDFORGE_DATA_DIR"] = str(_TMP)
os.environ["TRENDFORGE_DATABASE_PATH"] = str(_TMP / "test.db")
os.environ["TRENDFORGE_LOG_DIR"] = str(_TMP / "logs")

from app.db.migrate import run_migrations  # noqa: E402
from app.db.session import init_db  # noqa: E402

init_db()
run_migrations()
