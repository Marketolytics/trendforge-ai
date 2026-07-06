"""Keyword Intelligence (deterministic base).

Computes trending keywords, key phrases and emerging terms across a story
cluster. AI enrichment (synonyms, richer topic clusters) is layered on top.
"""

from __future__ import annotations

import re
from collections import Counter
from datetime import UTC, datetime, timedelta

from app.services.collectors.base import _STOPWORDS, extract_keywords, normalize_title

_WORD = re.compile(r"[a-z0-9][a-z0-9'\-]+")


def _ngrams(text: str, n: int) -> list[str]:
    words = [w for w in _WORD.findall(text.lower())]
    grams = []
    for i in range(len(words) - n + 1):
        window = words[i : i + n]
        if window[0] in _STOPWORDS or window[-1] in _STOPWORDS:
            continue
        grams.append(" ".join(window))
    return grams


def _as_utc(dt: datetime | None) -> datetime | None:
    if dt is None:
        return None
    return dt if dt.tzinfo else dt.replace(tzinfo=UTC)


def compute(members: list[dict]) -> dict:
    kw_counter: Counter = Counter()
    phrase_counter: Counter = Counter()
    recent_kw: Counter = Counter()
    older_kw: Counter = Counter()

    cutoff = datetime.now(UTC) - timedelta(hours=48)

    for m in members:
        title = m.get("title", "") or ""
        text = f"{title} {m.get('summary') or ''}"
        for kw in (m.get("keywords") or extract_keywords(text)):
            kw_counter[kw] += 1
        for phrase in _ngrams(title, 2) + _ngrams(title, 3):
            phrase_counter[phrase] += 1

        published = _as_utc(m.get("_published_dt"))
        bucket = recent_kw if (published and published >= cutoff) else older_kw
        for kw in extract_keywords(title, limit=6):
            bucket[kw] += 1

    # Emerging = keywords strong in the last 48h but not established earlier.
    emerging = [k for k, c in recent_kw.most_common(20) if older_kw.get(k, 0) <= c][:10]

    return {
        "trending": [{"word": w, "count": c} for w, c in kw_counter.most_common(15)],
        "search_phrases": [p for p, c in phrase_counter.most_common(12) if c >= 2][:10]
        or [p for p, _ in phrase_counter.most_common(8)],
        "emerging": emerging,
        "topic_clusters": _topic_clusters(kw_counter),
    }


def _topic_clusters(counter: Counter) -> list[dict]:
    """Group the strongest keywords into a few naive clusters by shared stems."""
    top = [w for w, _ in counter.most_common(12)]
    clusters: list[dict] = []
    used: set[str] = set()
    for anchor in top:
        if anchor in used:
            continue
        group = [anchor]
        used.add(anchor)
        for other in top:
            if other in used:
                continue
            if anchor[:4] == other[:4] or normalize_title(anchor) in normalize_title(other):
                group.append(other)
                used.add(other)
        clusters.append({"label": anchor, "keywords": group})
    return clusters[:5]
