from __future__ import annotations

import time
from typing import Optional

from fastapi import APIRouter

from superllm.config.settings import settings, Mode
from superllm.inference.router import InferenceRouter

router = APIRouter()
_router_engine: Optional[InferenceRouter] = None


def get_router():
    global _router_engine
    if _router_engine is None:
        _router_engine = InferenceRouter()
    return _router_engine


@router.get("/health")
async def health():
    engine = get_router()
    try:
        provider_health = await engine.health()
        return {
            "status": "healthy",
            "version": "0.1.0",
            "mode": settings.mode.value,
            "provider": provider_health.name,
            "provider_healthy": provider_health.healthy,
            "latency_ms": provider_health.latency_ms,
            "provider_error": provider_health.error,
        }
    except Exception as e:
        return {
            "status": "degraded",
            "version": "0.1.0",
            "mode": settings.mode.value,
            "provider": "none",
            "provider_healthy": False,
            "provider_error": str(e),
        }


@router.get("/status")
async def status():
    engine = get_router()
    provider_health = await engine.health()
    from superllm.models.registry import ModelRegistry
    registry = ModelRegistry.get_instance()
    stats = await registry.get_stats()
    return {
        "mode": settings.mode.value,
        "running": provider_health.healthy,
        "models": stats,
        "provider": provider_health.name,
        "provider_healthy": provider_health.healthy,
        "ui_enabled": settings.ui_enabled,
        "auth_enabled": settings.auth_enabled,
        "version": "0.1.0",
    }


@router.get("/api/status")
async def api_status():
    return await status()
