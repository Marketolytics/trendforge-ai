"""Competitor intelligence endpoints."""

from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, ConfigDict

from app.services.intelligence import competitors, patterns

router = APIRouter(prefix="/competitors", tags=["competitors"])


class ChannelOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    channel_id: str
    name: str
    handle: str
    thumbnail: str | None
    category: str
    video_count: int
    last_refreshed: datetime | None
    created_at: datetime


class VideoOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    channel_pk: int
    video_id: str
    title: str
    url: str | None
    thumbnail: str | None
    published: datetime | None
    views: int
    likes: int | None
    comments: int | None
    duration_seconds: int | None
    category: str


class AddChannel(BaseModel):
    handle: str
    category: str = "general"


@router.get("", response_model=list[ChannelOut])
def list_channels() -> list[ChannelOut]:
    return [ChannelOut.model_validate(c) for c in competitors.list_channels()]


@router.post("", response_model=ChannelOut, status_code=201)
async def add_channel(payload: AddChannel) -> ChannelOut:
    try:
        channel = await competitors.add_channel(payload.handle, payload.category)
    except competitors.ChannelResolveError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return ChannelOut.model_validate(channel)


@router.post("/refresh")
async def refresh_all() -> dict:
    return await competitors.refresh_all()


@router.post("/{channel_pk}/refresh")
async def refresh_one(channel_pk: int) -> dict:
    stored = await competitors.refresh_channel(channel_pk)
    return {"channel_pk": channel_pk, "new_videos": stored}


@router.delete("/{channel_pk}", status_code=204)
def delete_channel(channel_pk: int) -> None:
    if not competitors.delete_channel(channel_pk):
        raise HTTPException(status_code=404, detail="Channel not found")


@router.get("/videos", response_model=list[VideoOut])
def all_videos(limit: int = Query(300, ge=1, le=1000)) -> list[VideoOut]:
    return [VideoOut.model_validate(v) for v in competitors.get_videos(None, limit)]


@router.get("/patterns")
def channel_patterns(channel_pk: int | None = Query(None)) -> dict:
    return patterns.compute_patterns(channel_pk)


@router.get("/{channel_pk}/videos", response_model=list[VideoOut])
def channel_videos(channel_pk: int, limit: int = Query(200, ge=1, le=1000)) -> list[VideoOut]:
    return [VideoOut.model_validate(v) for v in competitors.get_videos(channel_pk, limit)]
