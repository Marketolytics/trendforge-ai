"""Build metadata.

A deployment/CI pipeline may write ``build_info.json`` next to the backend root
to record version, build date, commit and channel. In development the file is
absent and sensible defaults are returned.
"""

from __future__ import annotations

import json
from functools import lru_cache

from app.config import BASE_DIR, settings


@lru_cache
def build_info() -> dict:
    info = {
        "name": settings.app_name,
        "version": settings.version,
        "build_date": "",
        "commit": "",
        "channel": "dev",
    }
    path = BASE_DIR / "build_info.json"
    try:
        info.update(json.loads(path.read_text(encoding="utf-8")))
    except Exception:  # noqa: BLE001 - absent/invalid in dev
        pass
    return info
