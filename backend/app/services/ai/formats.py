"""Supported content formats and their pacing guidance."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Format:
    key: str
    label: str
    seconds: int
    kind: str  # "short" | "long"
    scene_hint: str


FORMATS: dict[str, Format] = {
    "15s": Format("15s", "15s Short", 15, "short", "3-4 fast scenes, instant hook"),
    "20s": Format("20s", "20s Short", 20, "short", "4-5 scenes"),
    "30s": Format("30s", "30s Short", 30, "short", "5-6 scenes"),
    "45s": Format("45s", "45s Short", 45, "short", "6-8 scenes"),
    "60s": Format("60s", "60s Short", 60, "short", "8-10 scenes, one clear payoff"),
    "3min": Format("3min", "3 Minute Video", 180, "long", "6-9 chapters/scenes"),
    "5min": Format("5min", "5 Minute Video", 300, "long", "8-12 chapters/scenes"),
    "8min": Format("8min", "8 Minute Video", 480, "long", "10-15 chapters/scenes"),
    "10min": Format("10min", "10 Minute Video", 600, "long", "12-18 chapters/scenes"),
}

DEFAULT_FORMAT = "60s"

VOICE_STYLES = [
    "Energetic",
    "News",
    "Storytelling",
    "Suspense",
    "Documentary",
    "Gaming",
    "Professional",
]


def get_format(key: str) -> Format:
    return FORMATS.get(key, FORMATS[DEFAULT_FORMAT])
