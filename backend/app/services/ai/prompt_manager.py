"""Prompt manager.

Loads versioned prompt templates from ``prompt_library/*.md``. Templates carry
YAML-style front matter (``version``, ``description``, ``temperature``) and a
body with ``{{variable}}`` placeholders. Templates are hot-reloaded when the
file changes on disk, so prompts stay editable without a restart.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from app.core.logging import get_logger

log = get_logger("trendforge.ai.prompts")

LIBRARY_DIR = Path(__file__).resolve().parent / "prompt_library"
_FRONT_MATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)
_VAR_RE = re.compile(r"\{\{\s*(\w+)\s*\}\}")


@dataclass
class PromptTemplate:
    name: str
    version: str
    description: str
    temperature: float
    body: str

    def render(self, context: dict[str, Any]) -> str:
        """Substitute {{vars}}; unknown vars render as empty strings."""

        def repl(match: re.Match[str]) -> str:
            key = match.group(1)
            value = context.get(key, "")
            return "" if value is None else str(value)

        return _VAR_RE.sub(repl, self.body).strip()


class PromptManager:
    """Loads and caches prompt templates with mtime-based hot reload."""

    def __init__(self, library_dir: Path = LIBRARY_DIR) -> None:
        self._dir = library_dir
        self._cache: dict[str, tuple[float, PromptTemplate]] = {}

    def _parse(self, name: str, text: str) -> PromptTemplate:
        version, description, temperature = "1.0.0", "", 0.6
        body = text
        match = _FRONT_MATTER_RE.match(text)
        if match:
            body = text[match.end():]
            for line in match.group(1).splitlines():
                if ":" not in line:
                    continue
                key, _, value = line.partition(":")
                key, value = key.strip(), value.strip()
                if key == "version":
                    version = value
                elif key == "description":
                    description = value
                elif key == "temperature":
                    try:
                        temperature = float(value)
                    except ValueError:
                        pass
        return PromptTemplate(name, version, description, temperature, body.strip())

    def get(self, name: str) -> PromptTemplate:
        path = self._dir / f"{name}.md"
        if not path.exists():
            raise FileNotFoundError(f"Prompt template not found: {name}")
        mtime = path.stat().st_mtime
        cached = self._cache.get(name)
        if cached and cached[0] == mtime:
            return cached[1]
        template = self._parse(name, path.read_text(encoding="utf-8"))
        self._cache[name] = (mtime, template)
        log.debug("loaded prompt", extra={"category": "ai", "prompt": name, "version": template.version})
        return template

    def render(self, name: str, context: dict[str, Any]) -> tuple[str, PromptTemplate]:
        template = self.get(name)
        return template.render(context), template

    def list_templates(self) -> list[dict[str, str]]:
        result: list[dict[str, str]] = []
        for path in sorted(self._dir.glob("*.md")):
            tpl = self.get(path.stem)
            result.append({"name": tpl.name, "version": tpl.version, "description": tpl.description})
        return result

    def variables(self, name: str) -> list[str]:
        """Return the distinct ``{{variable}}`` names used by a template."""
        template = self.get(name)
        seen: list[str] = []
        for match in _VAR_RE.finditer(template.body):
            var = match.group(1)
            if var not in seen:
                seen.append(var)
        return seen

    def validate(self, name: str, context: dict) -> dict:
        """Validate a template renders with the given context."""
        variables = self.variables(name)
        missing = [v for v in variables if context.get(v) in (None, "")]
        rendered = self.get(name).render(context)
        return {
            "name": name,
            "variables": variables,
            "missing": missing,
            "valid": "{{" not in rendered,
            "rendered_chars": len(rendered),
        }


prompt_manager = PromptManager()
