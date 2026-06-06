from __future__ import annotations

from typing import Optional

from fastapi import APIRouter
from pydantic import BaseModel

from superllm.config.settings import settings, Mode

router = APIRouter()


@router.get("/config")
async def get_config():
    return {
        "mode": settings.mode.value,
        "debug": settings.debug,
        "host": settings.host,
        "port": settings.port,
        "data_dir": str(settings.data_dir),
        "models_dir": str(settings.models_dir),
        "local_inference": settings.local_inference,
        "cloud_routing": settings.cloud_routing,
        "cloud_fallback": settings.cloud_fallback,
        "auth_enabled": settings.auth_enabled,
        "ui_enabled": settings.ui_enabled,
        "default_model": settings.default_model,
        "database_url": settings.database_url,
    }


class ConfigUpdate(BaseModel):
    mode: Optional[str] = None
    debug: Optional[bool] = None
    host: Optional[str] = None
    port: Optional[int] = None
    local_inference: Optional[bool] = None
    cloud_routing: Optional[bool] = None
    cloud_fallback: Optional[bool] = None
    auth_enabled: Optional[bool] = None
    ui_enabled: Optional[bool] = None
    default_model: Optional[str] = None


@router.post("/config")
async def update_config(update: ConfigUpdate):
    if update.mode is not None:
        settings.mode = Mode(update.mode)
    if update.debug is not None:
        settings.debug = update.debug
    if update.host is not None:
        settings.host = update.host
    if update.port is not None:
        settings.port = update.port
    if update.local_inference is not None:
        settings.local_inference = update.local_inference
    if update.cloud_routing is not None:
        settings.cloud_routing = update.cloud_routing
    if update.cloud_fallback is not None:
        settings.cloud_fallback = update.cloud_fallback
    if update.auth_enabled is not None:
        settings.auth_enabled = update.auth_enabled
    if update.ui_enabled is not None:
        settings.ui_enabled = update.ui_enabled
    if update.default_model is not None:
        settings.default_model = update.default_model
    return {"status": "updated", "config": await get_config()}
