"""Favorites: save and retrieve any item (trend, script, prompt, hook, ...)."""

from __future__ import annotations

from sqlmodel import Session, select

from app.db.models import Favorite
from app.db.session import engine


def add(type: str, label: str, ref_id: int | None = None, payload: dict | None = None) -> Favorite:
    with Session(engine) as session:
        fav = Favorite(type=type, label=label, ref_id=ref_id, payload=payload or {})
        session.add(fav)
        session.commit()
        session.refresh(fav)
        return fav


def list_favorites(type: str | None = None, q: str | None = None) -> list[Favorite]:
    with Session(engine) as session:
        stmt = select(Favorite)
        if type:
            stmt = stmt.where(Favorite.type == type)
        if q:
            stmt = stmt.where(Favorite.label.ilike(f"%{q}%"))
        stmt = stmt.order_by(Favorite.created_at.desc())
        return list(session.exec(stmt).all())


def delete(fav_id: int) -> bool:
    with Session(engine) as session:
        fav = session.get(Favorite, fav_id)
        if fav is None:
            return False
        session.delete(fav)
        session.commit()
        return True
