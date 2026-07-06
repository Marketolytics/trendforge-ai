"""Export generated modules as Markdown or a bundled ZIP package."""

from __future__ import annotations

import io
import json
import re
import zipfile
from datetime import UTC, datetime

KIND_LABELS: dict[str, str] = {
    "script": "Script",
    "storyboard": "Storyboard",
    "continuity": "Continuity Bible",
    "image_prompts": "Nano Banana Image Prompts",
    "video_prompts": "Video Prompts",
    "voiceover": "Voice Over",
    "broll": "B-Roll Suggestions",
    "thumbnail_blueprint": "Thumbnail Blueprint",
    "seo_package": "SEO Package",
    "checklist": "Production Checklist",
    "analysis": "Trend Analysis",
    "summary": "Summary",
    "strategy": "Content Strategy",
    "hooks": "Hooks",
    "titles": "Titles",
}


def _slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:60] or "trend"


def _label(key: str) -> str:
    return key.replace("_", " ").title()


def _render_list(items: list, level: int) -> list[str]:
    lines: list[str] = []
    for idx, item in enumerate(items, 1):
        if isinstance(item, dict):
            heading = item.get("number") or item.get("scene_number") or idx
            lines.append(f"{'#' * min(level, 6)} {heading}")
            lines.extend(_render_dict(item, level + 1))
            lines.append("")
        else:
            lines.append(f"- {item}")
    return lines


def _render_dict(data: dict, level: int) -> list[str]:
    lines: list[str] = []
    for key, value in data.items():
        if key in {"number", "scene_number"}:
            continue
        label = _label(key)
        if value in ("", None, [], {}):
            continue
        if isinstance(value, (str, int, float, bool)):
            lines.append(f"**{label}:** {value}")
        elif isinstance(value, list):
            lines.append(f"{'#' * min(level, 6)} {label}")
            lines.extend(_render_list(value, level + 1))
        elif isinstance(value, dict):
            lines.append(f"{'#' * min(level, 6)} {label}")
            lines.extend(_render_dict(value, level + 1))
    return lines


def to_markdown(kind: str, data: dict) -> str:
    label = KIND_LABELS.get(kind, _label(kind))
    body = "\n".join(_render_dict(data, 2)) if isinstance(data, dict) else str(data)
    return f"# {label}\n\n{body}\n"


def export_single(kind: str, data: dict, trend_title: str, fmt: str = "md") -> tuple[str, str, str]:
    """Return (filename, content, media_type) for a single module."""
    base = f"{_slug(trend_title)}-{kind}"
    if fmt == "json":
        return f"{base}.json", json.dumps(data, indent=2, ensure_ascii=False), "application/json"
    return f"{base}.md", to_markdown(kind, data), "text/markdown"


def export_zip(trend_title: str, format_label: str, modules: dict[str, dict]) -> tuple[str, bytes]:
    """Bundle every module into a ZIP (Markdown per module + package.json)."""
    buffer = io.BytesIO()
    generated = datetime.now(UTC).isoformat()

    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        index = [
            f"# {trend_title} — Production Package",
            "",
            f"- Format: {format_label}",
            f"- Generated: {generated}",
            f"- Modules: {len(modules)}",
            "",
            "## Contents",
        ]
        raw: dict[str, dict] = {}
        for kind, env in modules.items():
            data = env.get("data", env)
            raw[kind] = data
            filename = f"{kind}.md"
            zf.writestr(filename, to_markdown(kind, data))
            index.append(f"- `{filename}` — {KIND_LABELS.get(kind, kind)}")

        zf.writestr("README.md", "\n".join(index) + "\n")
        zf.writestr("package.json", json.dumps(raw, indent=2, ensure_ascii=False))

    filename = f"{_slug(trend_title)}-{_slug(format_label)}-package.zip"
    return filename, buffer.getvalue()
