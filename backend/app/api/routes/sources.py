"""Trend source management endpoints."""

from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, ConfigDict
from sqlmodel import Session, select

from app.db.models import TrendSource
from app.db.session import engine

router = APIRouter(prefix="/sources", tags=["sources"])


class SourceOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    type: str
    category: str
    config: dict
    enabled: bool
    created_at: datetime


class SourceCreate(BaseModel):
    name: str
    type: str
    category: str = "general"
    config: dict = {}
    enabled: bool = True


class SourceUpdate(BaseModel):
    name: str | None = None
    category: str | None = None
    config: dict | None = None
    enabled: bool | None = None


@router.get("", response_model=list[SourceOut])
def list_sources() -> list[SourceOut]:
    with Session(engine) as session:
        rows = session.exec(select(TrendSource).order_by(TrendSource.name)).all()
        return [SourceOut.model_validate(r) for r in rows]


@router.post("", response_model=SourceOut, status_code=201)
def create_source(payload: SourceCreate) -> SourceOut:
    with Session(engine) as session:
        source = TrendSource(**payload.model_dump())
        session.add(source)
        session.commit()
        session.refresh(source)
        return SourceOut.model_validate(source)


@router.patch("/{source_id}", response_model=SourceOut)
def update_source(source_id: int, payload: SourceUpdate) -> SourceOut:
    with Session(engine) as session:
        source = session.get(TrendSource, source_id)
        if source is None:
            raise HTTPException(status_code=404, detail="Source not found")
        for key, value in payload.model_dump(exclude_unset=True).items():
            setattr(source, key, value)
        session.add(source)
        session.commit()
        session.refresh(source)
        return SourceOut.model_validate(source)


@router.delete("/{source_id}", status_code=204)
def delete_source(source_id: int) -> None:
    with Session(engine) as session:
        source = session.get(TrendSource, source_id)
        if source is None:
            raise HTTPException(status_code=404, detail="Source not found")
        session.delete(source)
        session.commit()
