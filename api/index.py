"""Vercel serverless entry point for the FastAPI backend.

Vercel's Python runtime (@vercel/python) serves an ASGI application exported as
``app``. Requests are routed here by the ``/api/(.*)`` rewrite in ``vercel.json``;
the app receives the original path (``/api/...``), which matches FastAPI's routes.

The backend package lives in ``../backend`` and is bundled into the function via
the ``includeFiles`` setting in ``vercel.json``.
"""

from __future__ import annotations

import os
import sys

_BACKEND = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "backend")
if _BACKEND not in sys.path:
    sys.path.insert(0, _BACKEND)

from app.main import app  # noqa: E402  (path set up above)

# Ensure one-time startup (DB schema/seed) runs in the serverless environment,
# since ASGI lifespan is not guaranteed to fire on every platform.
from app.main import initialize  # noqa: E402

initialize()

__all__ = ["app"]
