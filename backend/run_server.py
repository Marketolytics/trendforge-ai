"""Portable server entrypoint.

Runs the FastAPI app with a configurable host/port. This is the entrypoint the
desktop launcher (Tauri) spawns — both in development (via Python) and in a
packaged build (via the PyInstaller-built sidecar executable).

Usage:
    python run_server.py --host 127.0.0.1 --port 8756
"""

from __future__ import annotations

import argparse
import sys

import uvicorn

from app.config import settings


def main() -> None:
    parser = argparse.ArgumentParser(description="TrendForge AI backend")
    parser.add_argument("--host", default=settings.host)
    parser.add_argument("--port", type=int, default=settings.port)
    parser.add_argument("--log-level", default=settings.log_level.lower())
    args = parser.parse_args()

    # Ensure the workspace exists before serving (first-run safe).
    settings.ensure_dirs()

    # Import the app object directly so this works when frozen (no reload).
    from app.main import app

    print(f"TrendForge backend starting on http://{args.host}:{args.port}", file=sys.stderr, flush=True)
    uvicorn.run(app, host=args.host, port=args.port, log_level=args.log_level)


if __name__ == "__main__":
    main()
