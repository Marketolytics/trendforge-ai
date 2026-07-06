"""Entity recognition (deterministic base).

A lightweight, dependency-free recognizer using known gaming vocabularies plus
Title-Case phrase detection. The AI verification layer produces the full typed
entity set; this gives an instant, offline-capable base.
"""

from __future__ import annotations

import re
from collections import Counter

PLATFORMS = {
    "ps5", "ps4", "playstation", "xbox", "xbox series x", "xbox series s", "pc",
    "steam", "nintendo switch", "switch", "steam deck", "steam machine", "epic games",
}
COMPANIES = {
    "rockstar", "rockstar games", "sony", "microsoft", "nintendo", "valve", "ubisoft",
    "electronic arts", "ea", "activision", "blizzard", "bethesda", "cd projekt",
    "square enix", "capcom", "sega", "epic", "riot games", "naughty dog",
}

_TITLECASE = re.compile(r"\b([A-Z][a-zA-Z0-9']+(?:\s+[A-Z][a-zA-Z0-9':]+){0,3})\b")

# Pre-compile word-boundary matchers so short terms (ea, pc) don't match
# substrings inside unrelated words (e.g. "real").
_PLATFORM_RES = {p: re.compile(rf"\b{re.escape(p)}\b", re.IGNORECASE) for p in PLATFORMS}
_COMPANY_RES = {c: re.compile(rf"\b{re.escape(c)}\b", re.IGNORECASE) for c in COMPANIES}


def extract(members: list[dict]) -> dict:
    platforms: Counter = Counter()
    companies: Counter = Counter()
    titles_phrases: Counter = Counter()

    for m in members:
        title = m.get("title", "") or ""
        for p, rx in _PLATFORM_RES.items():
            if rx.search(title):
                platforms[p.title()] += 1
        for c, rx in _COMPANY_RES.items():
            if rx.search(title):
                companies[c.title()] += 1
        for phrase in _TITLECASE.findall(title):
            if len(phrase) > 3 and phrase.lower() not in PLATFORMS and phrase.lower() not in COMPANIES:
                titles_phrases[phrase] += 1

    # Candidate games/topics = most frequent Title-Case phrases.
    topics = [{"name": p, "count": c} for p, c in titles_phrases.most_common(12)]

    return {
        "platforms": [p for p, _ in platforms.most_common()],
        "companies": [c for c, _ in companies.most_common()],
        "topics": topics,
    }
