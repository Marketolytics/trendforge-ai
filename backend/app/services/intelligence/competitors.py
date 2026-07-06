"""Competitor intelligence.

Save YouTube channels and collect their recent videos. Uses the public
per-channel Atom feed (no API key). RSS exposes title, url, publish time,
thumbnail and view count; likes/comments/duration are not available without the
official API and are stored as null.
"""

from __future__ import annotations

import asyncio
import re
from datetime import datetime, timezone
from time import mktime

import feedparser
import httpx

from app.core.logging import get_logger, log_network_error
from app.db.models import CompetitorChannel, CompetitorVideo, utcnow
from app.db.session import engine
from app.services.collectors.net import USER_AGENT, fetch_text
from sqlmodel import Session, select

log = get_logger("trendforge.intelligence.competitors")

RSS_URL = "https://www.youtube.com/feeds/videos.xml?channel_id={cid}"
_CHANNEL_ID_RE = re.compile(r"UC[0-9A-Za-z_-]{22}")
_PAGE_ID_RE = re.compile(r'"(?:channelId|externalId)":"(UC[0-9A-Za-z_-]{22})"')
_OG_TITLE_RE = re.compile(r'<meta property="og:title" content="([^"]+)"')
_OG_IMAGE_RE = re.compile(r'<meta property="og:image" content="([^"]+)"')


class ChannelResolveError(Exception):
    pass


async def _resolve_channel(handle: str) -> tuple[str, str, str | None]:
    """Resolve arbitrary channel input to (channel_id, name, thumbnail)."""
    handle = handle.strip()

    # Direct channel id.
    if re.fullmatch(r"UC[0-9A-Za-z_-]{22}", handle):
        cid = handle
    elif "/channel/" in handle:
        m = _CHANNEL_ID_RE.search(handle)
        if not m:
            raise ChannelResolveError("Could not read channel id from URL")
        cid = m.group(0)
    else:
        # Handle (@name), custom URL or full URL -> fetch the page and extract.
        url = handle
        if handle.startswith("@"):
            url = f"https://www.youtube.com/{handle}"
        elif not handle.startswith("http"):
            url = f"https://www.youtube.com/@{handle}"
        try:
            html = await fetch_text(url, ttl_seconds=86400, headers={"User-Agent": USER_AGENT})
        except Exception as exc:  # noqa: BLE001
            raise ChannelResolveError(f"Could not load channel page: {exc}") from exc
        m = _PAGE_ID_RE.search(html)
        if not m:
            raise ChannelResolveError("Could not find a channel id on that page")
        cid = m.group(1)
        name_m = _OG_TITLE_RE.search(html)
        img_m = _OG_IMAGE_RE.search(html)
        return cid, (name_m.group(1) if name_m else cid), (img_m.group(1) if img_m else None)

    # For direct ids/urls, pull name/thumb from the RSS feed title later.
    return cid, "", None


def _entry_video_id(entry) -> str | None:
    vid = entry.get("yt_videoid")
    if vid:
        return vid
    link = entry.get("link", "")
    m = re.search(r"[?&]v=([\w-]+)", link)
    if m:
        return m.group(1)
    ident = entry.get("id", "")
    return ident.split(":")[-1] if ident else None


def _views(entry) -> int:
    stats = entry.get("media_statistics") or {}
    try:
        return int(stats.get("views", 0))
    except (TypeError, ValueError):
        return 0


async def add_channel(handle: str, category: str = "general") -> CompetitorChannel:
    """Resolve, persist and populate a competitor channel."""
    channel_id, name, thumb = await _resolve_channel(handle)

    with Session(engine) as session:
        existing = session.exec(
            select(CompetitorChannel).where(CompetitorChannel.channel_id == channel_id)
        ).first()
        if existing is not None:
            return existing
        channel = CompetitorChannel(
            channel_id=channel_id,
            name=name or channel_id,
            handle=handle,
            thumbnail=thumb,
            category=category,
        )
        session.add(channel)
        session.commit()
        session.refresh(channel)
        pk = channel.id

    await refresh_channel(pk)
    with Session(engine) as session:
        return session.get(CompetitorChannel, pk)  # type: ignore[return-value]


async def refresh_channel(channel_pk: int) -> int:
    """Fetch the channel RSS feed and upsert its recent videos."""
    with Session(engine) as session:
        channel = session.get(CompetitorChannel, channel_pk)
        if channel is None:
            return 0
        cid = channel.channel_id
        category = channel.category

    url = RSS_URL.format(cid=cid)
    try:
        raw = await fetch_text(url, ttl_seconds=1800, headers={"User-Agent": USER_AGENT})
    except Exception as exc:  # noqa: BLE001
        log_network_error(cid, url, exc)
        return 0

    parsed = await asyncio.to_thread(feedparser.parse, raw)
    feed_title = parsed.feed.get("title") if parsed.feed else None

    stored = 0
    with Session(engine) as session:
        channel = session.get(CompetitorChannel, channel_pk)
        if channel is None:
            return 0
        if (not channel.name or channel.name == channel.channel_id) and feed_title:
            channel.name = feed_title

        for entry in parsed.entries:
            vid = _entry_video_id(entry)
            if not vid:
                continue
            existing = session.exec(
                select(CompetitorVideo).where(CompetitorVideo.video_id == vid)
            ).first()
            published = None
            if entry.get("published_parsed"):
                try:
                    published = datetime.fromtimestamp(
                        mktime(entry["published_parsed"]), tz=timezone.utc
                    )
                except (OverflowError, ValueError):
                    published = None
            thumb = None
            media = entry.get("media_thumbnail")
            if media and isinstance(media, list) and media[0].get("url"):
                thumb = media[0]["url"]

            if existing is None:
                session.add(
                    CompetitorVideo(
                        channel_pk=channel_pk,
                        video_id=vid,
                        title=entry.get("title", "").strip(),
                        url=entry.get("link"),
                        thumbnail=thumb,
                        published=published,
                        views=_views(entry),
                        category=category,
                    )
                )
                stored += 1
            else:
                existing.views = _views(entry) or existing.views
                existing.collected_at = utcnow()
                session.add(existing)

        count = session.exec(
            select(CompetitorVideo).where(CompetitorVideo.channel_pk == channel_pk)
        ).all()
        channel.video_count = len(count)
        channel.last_refreshed = utcnow()
        session.add(channel)
        session.commit()

    return stored


async def refresh_all() -> dict:
    with Session(engine) as session:
        pks = [c.id for c in session.exec(select(CompetitorChannel)).all() if c.id]
    results = await asyncio.gather(*(refresh_channel(pk) for pk in pks), return_exceptions=True)
    total = sum(r for r in results if isinstance(r, int))
    return {"channels": len(pks), "new_videos": total}


def list_channels() -> list[CompetitorChannel]:
    with Session(engine) as session:
        return list(session.exec(select(CompetitorChannel).order_by(CompetitorChannel.name)).all())


def get_videos(channel_pk: int | None = None, limit: int = 200) -> list[CompetitorVideo]:
    with Session(engine) as session:
        stmt = select(CompetitorVideo)
        if channel_pk is not None:
            stmt = stmt.where(CompetitorVideo.channel_pk == channel_pk)
        stmt = stmt.order_by(CompetitorVideo.published.desc()).limit(limit)
        return list(session.exec(stmt).all())


def delete_channel(channel_pk: int) -> bool:
    with Session(engine) as session:
        channel = session.get(CompetitorChannel, channel_pk)
        if channel is None:
            return False
        for v in session.exec(
            select(CompetitorVideo).where(CompetitorVideo.channel_pk == channel_pk)
        ).all():
            session.delete(v)
        session.delete(channel)
        session.commit()
        return True
