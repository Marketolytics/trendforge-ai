"""Structured, rotating logging for TrendForge AI.

Logs are written as JSON lines to the local log directory and rotated
automatically. A separate error log captures WARNING+ records. Helper
functions provide consistent categories:

    errors, ai, refresh, network, performance

Usage:
    from app.core.logging import get_logger, log_event
    log = get_logger("trendforge.refresh")
    log.info("refresh started", extra={"category": "refresh", "sources": 6})
"""

from __future__ import annotations

import json
import logging
import time
from contextlib import contextmanager
from logging.handlers import RotatingFileHandler
from typing import Any

from app.config import settings

_CONFIGURED = False

# Reserved LogRecord attributes we don't want duplicated in the "extra" dump.
_RESERVED = set(
    logging.makeLogRecord({}).__dict__.keys()
) | {"message", "asctime", "category", "taskName"}


class JsonFormatter(logging.Formatter):
    """Render log records as single-line JSON with structured extras."""

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "ts": self.formatTime(record, "%Y-%m-%dT%H:%M:%S%z"),
            "level": record.levelname,
            "logger": record.name,
            "category": getattr(record, "category", "general"),
            "message": record.getMessage(),
        }
        # Merge any custom structured fields passed via `extra=`.
        for key, value in record.__dict__.items():
            if key not in _RESERVED and not key.startswith("_"):
                payload[key] = value
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload, default=str, ensure_ascii=False)


def configure_logging() -> None:
    """Configure root logging handlers. Idempotent."""
    global _CONFIGURED
    if _CONFIGURED:
        return

    level = getattr(logging, settings.log_level.upper(), logging.INFO)
    root = logging.getLogger()
    root.setLevel(level)

    json_fmt = JsonFormatter()

    # Avoid duplicate handlers on reload.
    root.handlers.clear()

    # On serverless hosts (Vercel) the filesystem is read-only/ephemeral, so log
    # structured JSON to stdout — the platform captures it. Elsewhere, also write
    # rotating files for local inspection.
    if settings.is_serverless:
        stdout = logging.StreamHandler()
        stdout.setFormatter(json_fmt)
        stdout.setLevel(level)
        root.addHandler(stdout)
    else:
        try:
            log_dir = settings.resolved_log_dir
            log_dir.mkdir(parents=True, exist_ok=True)

            # Rotating combined log (5 files x 2 MB).
            app_handler = RotatingFileHandler(
                log_dir / "trendforge.log", maxBytes=2_000_000, backupCount=5, encoding="utf-8"
            )
            app_handler.setFormatter(json_fmt)
            app_handler.setLevel(level)

            # Dedicated error log (WARNING and above).
            err_handler = RotatingFileHandler(
                log_dir / "errors.log", maxBytes=2_000_000, backupCount=5, encoding="utf-8"
            )
            err_handler.setFormatter(json_fmt)
            err_handler.setLevel(logging.WARNING)

            root.addHandler(app_handler)
            root.addHandler(err_handler)
        except OSError:
            # Read-only FS we didn't detect — fall back to stdout only.
            pass

        # Human-readable console output for local development.
        console = logging.StreamHandler()
        console.setFormatter(
            logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
        )
        console.setLevel(level)
        root.addHandler(console)

    # Tame noisy third-party loggers.
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)

    _CONFIGURED = True


def get_logger(name: str = "trendforge") -> logging.Logger:
    return logging.getLogger(name)


# --- Category helpers -----------------------------------------------------

def log_event(category: str, message: str, level: int = logging.INFO, **fields: Any) -> None:
    """Emit a categorized structured log line."""
    logging.getLogger(f"trendforge.{category}").log(
        level, message, extra={"category": category, **fields}
    )


def log_network_error(source: str, url: str, error: Exception) -> None:
    log_event(
        "network",
        f"network error collecting {source}",
        level=logging.WARNING,
        source=source,
        url=url,
        error=str(error),
    )


def log_refresh(message: str, **fields: Any) -> None:
    log_event("refresh", message, **fields)


def log_ai(message: str, **fields: Any) -> None:
    log_event("ai", message, **fields)


@contextmanager
def performance(operation: str, **fields: Any):
    """Context manager that logs the duration of an operation."""
    start = time.perf_counter()
    try:
        yield
    finally:
        elapsed_ms = round((time.perf_counter() - start) * 1000, 1)
        log_event(
            "performance",
            f"{operation} completed",
            operation=operation,
            duration_ms=elapsed_ms,
            **fields,
        )
