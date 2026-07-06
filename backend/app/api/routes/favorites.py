"""Favorites endpoints."""

from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, ConfigDict

from app.services import favorites_service

router = APIRouter(prefix="/favorites", tags=["favorites"])


class FavoriteOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    type: str
    label: str
    ref_id: int | None
    payload: dict
    created_at: datetime


class FavoriteCreate(BaseModel):
    type: str
    label: str
    ref_id: int | None = None
    payload: dict = {}


@router.get("", response_model=list[FavoriteOut])
def list_favorites(
    type: str | None = Query(None), q: str | None = Query(None)
) -> list[FavoriteOut]:
    return [FavoriteOut.model_validate(f) for f in favorites_service.list_favorites(type, q)]


@router.post("", response_model=FavoriteOut, status_code=201)
def add_favorite(payload: FavoriteCreate) -> FavoriteOut:
    fav = favorites_service.add(payload.type, payload.label, payload.ref_id, payload.payload)
    return FavoriteOut.model_validate(fav)


@router.delete("/{fav_id}", status_code=204)
def delete_favorite(fav_id: int) -> None:
    if not favorites_service.delete(fav_id):
        raise HTTPException(status_code=404, detail="Favorite not found")
