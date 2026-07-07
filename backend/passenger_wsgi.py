"""Passenger WSGI entrypoint for Hostinger shared hosting.

Hostinger's "Setup Python App" runs applications through Phusion Passenger,
which expects a module exposing a WSGI callable named ``application``. TrendForge
is an ASGI (FastAPI) app, so we:

  1. run the idempotent startup routine (DB init, migrations, seed) — WSGI has
     no lifespan protocol, so this must happen here, and
  2. wrap the ASGI app with a2wsgi's ASGIMiddleware to expose it as WSGI.

Point the Python app's "Application startup file" at this file and the
"Application entry point" (callable) at ``application``.
"""

from __future__ import annotations

import os
import sys

# Ensure the backend package root is importable regardless of Passenger's cwd.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

# Load environment variables from a local .env if present (Passenger may not).
try:
    from dotenv import load_dotenv

    load_dotenv(os.path.join(BASE_DIR, ".env"))
except Exception:  # noqa: BLE001
    pass

from a2wsgi import ASGIMiddleware  # noqa: E402

from app.main import app as _asgi_app  # noqa: E402
from app.main import initialize  # noqa: E402

# Run startup work once at import time (WSGI has no lifespan events).
initialize()

# The WSGI callable Passenger will serve.
application = ASGIMiddleware(_asgi_app)
