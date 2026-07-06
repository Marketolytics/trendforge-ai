"""Prompt engine: loading, rendering, variables and validation."""

from __future__ import annotations

from app.services.ai.prompt_manager import prompt_manager


def test_templates_load_with_versions():
    templates = prompt_manager.list_templates()
    names = {t["name"] for t in templates}
    assert "script" in names and "research" in names and "trend_analysis" in names
    for t in templates:
        assert t["version"]


def test_render_substitutes_variables():
    rendered, tpl = prompt_manager.render(
        "script",
        {"title": "GTA 6", "summary": "s", "keywords": "gta", "category": "gaming",
         "format_label": "60s Short", "seconds": 60, "scene_hint": "8 scenes"},
    )
    assert "GTA 6" in rendered
    assert "{{" not in rendered
    assert tpl.version


def test_validate_reports_missing():
    result = prompt_manager.validate("script", {"title": "X"})
    assert "seconds" in result["variables"]
    assert "seconds" in result["missing"]
