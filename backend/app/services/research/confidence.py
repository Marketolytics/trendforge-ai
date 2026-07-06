"""Source Confidence Engine.

Assigns every source a confidence tier and numeric score so that an official
announcement is never weighted the same as community speculation.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Tier:
    key: str
    label: str
    score: int


TIERS: dict[str, Tier] = {
    "official": Tier("official", "Official", 95),
    "developer": Tier("developer", "Developer", 90),
    "industry": Tier("industry", "Industry News", 75),
    "community": Tier("community", "Community", 45),
    "forum": Tier("forum", "Forum", 40),
    "social": Tier("social", "Social", 35),
    "signal": Tier("signal", "Trend Signal", 30),
    "unknown": Tier("unknown", "Unknown", 25),
}

# Source type -> default tier.
_TYPE_TIER = {
    "steam": "official",
    "rockstar": "industry",       # collected via news aggregation, not the wire
    "gaming_news": "industry",
    "google_trends": "signal",
    "reddit": "community",
    "youtube": "social",
    "rss": "industry",
}

# Name hints that upgrade/override the tier.
_NAME_OFFICIAL = ("steam", "newswire", "official", "dev blog", "developer blog", "press release")
_NAME_INDUSTRY = ("ign", "polygon", "eurogamer", "gamespot", "pc gamer", "rock paper shotgun",
                  "kotaku", "vg247", "gamesradar", "google news")


def classify(source: str, source_type: str) -> Tier:
    name = (source or "").lower()
    if any(h in name for h in _NAME_OFFICIAL):
        return TIERS["official"]
    if any(h in name for h in _NAME_INDUSTRY):
        return TIERS["industry"]
    if name.startswith("r/"):
        return TIERS["community"]
    return TIERS[_TYPE_TIER.get(source_type, "unknown")]


def tier_meta() -> list[dict]:
    return [{"key": t.key, "label": t.label, "score": t.score} for t in TIERS.values()]
