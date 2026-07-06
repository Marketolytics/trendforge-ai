"""Response parser.

Gemini is asked for pure JSON, but models occasionally wrap output in markdown
fences or add stray text. This module extracts and repairs the JSON payload,
then validates it into a typed Pydantic model.
"""

from __future__ import annotations

import json
import re
from typing import TypeVar

from pydantic import BaseModel, ValidationError

from app.core.logging import get_logger

log = get_logger("trendforge.ai.parser")

T = TypeVar("T", bound=BaseModel)

_FENCE_RE = re.compile(r"```(?:json)?\s*(.*?)```", re.DOTALL)


class ResponseParseError(Exception):
    """Raised when a model response cannot be parsed into valid JSON."""


def extract_json(text: str) -> dict:
    """Extract a JSON object from raw model text, tolerating fences/noise."""
    if not text or not text.strip():
        raise ResponseParseError("empty response")

    candidate = text.strip()

    # 1) Prefer a fenced ```json block if present.
    fence = _FENCE_RE.search(candidate)
    if fence:
        candidate = fence.group(1).strip()

    # 2) Fast path.
    try:
        return json.loads(candidate)
    except json.JSONDecodeError:
        pass

    # 3) Slice from the first '{' to the last '}'.
    start = candidate.find("{")
    end = candidate.rfind("}")
    if start != -1 and end != -1 and end > start:
        snippet = candidate[start : end + 1]
        try:
            return json.loads(snippet)
        except json.JSONDecodeError:
            # 4) Last resort: strip trailing commas before } or ].
            repaired = re.sub(r",\s*([}\]])", r"\1", snippet)
            try:
                return json.loads(repaired)
            except json.JSONDecodeError as exc:
                raise ResponseParseError(f"invalid JSON: {exc}") from exc

    raise ResponseParseError("no JSON object found in response")


def parse_into(text: str, model: type[T]) -> T:
    """Extract JSON and validate it into ``model``."""
    data = extract_json(text)
    try:
        return model.model_validate(data)
    except ValidationError as exc:
        log.warning(
            "response failed schema validation",
            extra={"category": "ai", "model": model.__name__, "errors": exc.error_count()},
        )
        raise ResponseParseError(f"schema validation failed: {exc}") from exc
