"""Export rendering + ZIP packaging."""

from __future__ import annotations

import io
import zipfile

from app.services.ai.export import export_zip, to_markdown


def test_to_markdown_renders_fields():
    md = to_markdown("script", {"hook": "Wait for it", "segments": [{"label": "Setup", "text": "x"}]})
    assert "# Script" in md
    assert "Wait for it" in md


def test_export_zip_bundles_modules():
    modules = {
        "script": {"data": {"hook": "h", "full_script": "s"}},
        "seo_package": {"data": {"description": "d", "tags": ["t1"]}},
    }
    filename, data = export_zip("My Trend", "60s Short", modules)
    assert filename.endswith(".zip")
    with zipfile.ZipFile(io.BytesIO(data)) as zf:
        names = zf.namelist()
        assert "script.md" in names
        assert "seo_package.md" in names
        assert "package.json" in names
        assert "README.md" in names
