"""Local AI usage tracking (request counts + token estimates per provider)."""

from __future__ import annotations

from datetime import UTC, datetime

from sqlmodel import Session, select

from app.db.models import ProviderUsage
from app.db.session import engine


def record(provider: str, prompt_tokens: int, response_tokens: int) -> None:
    with Session(engine) as s:
        row = s.get(ProviderUsage, provider)
        if row is None:
            row = ProviderUsage(provider=provider)
        row.requests += 1
        row.prompt_tokens += max(prompt_tokens, 0)
        row.response_tokens += max(response_tokens, 0)
        row.last_success = datetime.now(UTC)
        s.add(row)
        s.commit()


def stats() -> list[dict]:
    with Session(engine) as s:
        rows = s.exec(select(ProviderUsage)).all()
        return [
            {
                "provider": r.provider,
                "requests": r.requests,
                "prompt_tokens": r.prompt_tokens,
                "response_tokens": r.response_tokens,
                "total_tokens": r.prompt_tokens + r.response_tokens,
                "last_success": r.last_success.isoformat() if r.last_success else None,
            }
            for r in rows
        ]
