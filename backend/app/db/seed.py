"""Default trend sources seeded on first launch.

All feeds/endpoints below are public and require no API key. Sources are
data-driven: the aggregation engine simply runs whatever is enabled here.
Users can add, edit, disable or remove sources later without code changes.
"""

from __future__ import annotations

from sqlmodel import Session, select

from app.core.logging import get_logger
from app.db.models import TrendSource
from app.db.session import engine

log = get_logger("trendforge.seed")

DEFAULT_SOURCES: list[dict] = [
    # --- Google Trends -------------------------------------------------
    {
        "name": "Google Trends (US)",
        "type": "google_trends",
        "category": "trending",
        "config": {"geo": "US", "limit": 25},
    },
    # --- Gaming news (RSS) --------------------------------------------
    {
        "name": "IGN",
        "type": "gaming_news",
        "category": "gaming",
        "config": {"feeds": ["https://feeds.ign.com/ign/all"], "limit": 25},
    },
    {
        "name": "PC Gamer",
        "type": "gaming_news",
        "category": "gaming",
        "config": {"feeds": ["https://www.pcgamer.com/rss/"], "limit": 25},
    },
    {
        "name": "Eurogamer",
        "type": "gaming_news",
        "category": "gaming",
        "config": {"feeds": ["https://www.eurogamer.net/feed"], "limit": 25},
    },
    {
        "name": "Polygon",
        "type": "gaming_news",
        "category": "gaming",
        "config": {"feeds": ["https://www.polygon.com/rss/index.xml"], "limit": 25},
    },
    {
        "name": "GameSpot",
        "type": "gaming_news",
        "category": "gaming",
        "config": {"feeds": ["https://www.gamespot.com/feeds/news/"], "limit": 25},
    },
    {
        "name": "Rock Paper Shotgun",
        "type": "gaming_news",
        "category": "gaming",
        "config": {"feeds": ["https://www.rockpapershotgun.com/feed"], "limit": 25},
    },
    # --- Reddit -------------------------------------------------------
    {
        "name": "Reddit Gaming",
        "type": "reddit",
        "category": "gaming",
        "config": {"subreddits": ["gaming", "Games", "pcgaming"], "limit": 20},
    },
    # --- Steam --------------------------------------------------------
    {
        "name": "Steam News",
        "type": "steam",
        "category": "gaming",
        "config": {
            "apps": [
                {"appid": 730, "name": "Counter-Strike 2"},
                {"appid": 570, "name": "Dota 2"},
                {"appid": 578080, "name": "PUBG"},
                {"appid": 271590, "name": "GTA V"},
            ],
            "count": 6,
        },
    },
    # --- YouTube (channel Atom feeds) ---------------------------------
    {
        "name": "YouTube · Gaming Channels",
        "type": "youtube",
        "category": "gaming",
        "config": {
            "channels": [
                "UCKy1dAqELo0zrOtPkf0eTMw",  # IGN
                "UCbu2SsF-Or3Rsn3NxqODImw",  # GameSpot
            ],
            "limit": 12,
        },
    },
    # --- Rockstar (Google News RSS query = reliable, key-free) --------
    {
        "name": "Rockstar Newswire",
        "type": "rockstar",
        "category": "gaming",
        "config": {
            "feeds": [
                "https://news.google.com/rss/search?q=Rockstar+Games+OR+GTA&hl=en-US&gl=US&ceid=US:en"
            ],
            "limit": 20,
        },
    },
]


def seed_sources() -> None:
    """Insert default sources only when none exist (first launch)."""
    with Session(engine) as session:
        if session.exec(select(TrendSource)).first() is not None:
            return
        for spec in DEFAULT_SOURCES:
            session.add(TrendSource(**spec))
        session.commit()
        log.info(
            "seeded default trend sources",
            extra={"category": "refresh", "count": len(DEFAULT_SOURCES)},
        )
