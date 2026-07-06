"""AI provider & model management endpoints."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.ai import credentials, usage
from app.services.ai import router as model_router
from app.services.ai.providers.registry import PROVIDERS, get_provider, provider_meta
from app.services.settings_service import SettingsService

router = APIRouter(prefix="/providers", tags=["providers"])


class KeyPayload(BaseModel):
    key: str


class ProviderConfig(BaseModel):
    provider: str | None = None
    model_research: str | None = None
    model_content: str | None = None
    model_quality: str | None = None


@router.get("")
def list_providers() -> dict:
    active = model_router.current_provider()
    providers = []
    for meta in provider_meta():
        p = PROVIDERS[meta["name"]]
        providers.append({
            **meta,
            "key_set": credentials.has_key(meta["name"]),
            "configured": p.is_configured(),
            "active": meta["name"] == active,
        })
    return {"active": active, "providers": providers}


@router.get("/config")
def get_config() -> dict:
    return {
        "provider": model_router.current_provider(),
        "models": {
            "research": model_router.model_for("research"),
            "content": model_router.model_for("content"),
            "quality": model_router.model_for("quality"),
        },
    }


@router.put("/config")
def set_config(payload: ProviderConfig) -> dict:
    updates: dict = {}
    if payload.provider is not None:
        if payload.provider not in PROVIDERS:
            raise HTTPException(status_code=400, detail="Unknown provider")
        updates["provider"] = payload.provider
    for cat in ("research", "content", "quality"):
        value = getattr(payload, f"model_{cat}")
        if value:
            updates[f"model_{cat}"] = value
    SettingsService.update(updates)
    return get_config()


@router.post("/{name}/key")
def set_key(name: str, payload: KeyPayload) -> dict:
    if name not in PROVIDERS:
        raise HTTPException(status_code=404, detail="Unknown provider")
    if not credentials.set_key(name, payload.key.strip()):
        raise HTTPException(status_code=500, detail="Could not store key in the OS credential store")
    return {"ok": True, "key_set": True}


@router.delete("/{name}/key", status_code=200)
def delete_key(name: str) -> dict:
    credentials.delete_key(name)
    return {"ok": True, "key_set": False}


@router.post("/{name}/test")
async def test_connection(name: str) -> dict:
    if name not in PROVIDERS:
        raise HTTPException(status_code=404, detail="Unknown provider")
    result = await get_provider(name).validate()
    return {
        "ok": result.ok,
        "latency_ms": result.latency_ms,
        "models": [{"id": m.id, "label": m.label} for m in result.models],
        "error": result.error,
    }


@router.get("/usage")
def get_usage() -> dict:
    return {
        "active_provider": model_router.current_provider(),
        "models": {
            "research": model_router.model_for("research"),
            "content": model_router.model_for("content"),
            "quality": model_router.model_for("quality"),
        },
        "usage": usage.stats(),
    }
