"""Model router.

Maps each AI task to a category (research / content / quality) and resolves the
provider + model to use from user settings. This is how different tasks route to
different models.
"""

from __future__ import annotations

from app.services.settings_service import SettingsService

# Task kind -> category. Unknown kinds default to "content".
_CATEGORY: dict[str, str] = {
    # research
    "analysis": "research",
    "summary": "research",
    "opportunity": "research",
    "forecast": "research",
    "upload_advisor": "research",
    "competitor_gap": "research",
    "research": "research",
    # quality
    "quality_review": "quality",
    # everything else is content generation
}

CATEGORIES = ("research", "content", "quality")


def category_for(kind: str) -> str:
    return _CATEGORY.get(kind, "content")


def current_provider() -> str:
    return SettingsService.get("provider") or "gemini"


def model_for(category: str) -> str:
    key = f"model_{category}" if category in CATEGORIES else "model_content"
    return SettingsService.get(key) or SettingsService.get("gemini_model") or "gemini-2.5-flash"
