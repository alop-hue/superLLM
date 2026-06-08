from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from superllm.providers.base import Provider
from superllm.providers.registry import registry

router = APIRouter()


class ProviderCreate(BaseModel):
    name: str
    provider_type: str
    base_url: Optional[str] = None
    api_key: Optional[str] = None
    default_model: Optional[str] = None
    is_enabled: bool = True
    priority: int = 0
    config: dict = {}


@router.get("/providers")
async def list_providers():
    providers = await registry.get_providers()
    return {
        "providers": [
            {
                "name": p.name,
                "provider_type": p.provider_type,
                "is_enabled": p.is_enabled,
                "priority": p.priority,
                "base_url": p.base_url,
                "api_key": p.api_key,
                "default_model": p.default_model,
                "config": p.config,
            }
            for p in providers
        ],
        "total": len(providers),
    }


@router.get("/providers/types")
async def list_provider_types():
    from superllm.config.settings import ProviderType
    return {
        "types": [t.value for t in ProviderType],
    }


@router.post("/providers")
async def add_provider(create: ProviderCreate):
    provider = Provider(
        name=create.name,
        provider_type=create.provider_type,
        base_url=create.base_url,
        api_key=create.api_key,
        default_model=create.default_model,
        is_enabled=create.is_enabled,
        priority=create.priority,
        config=create.config,
    )
    result = await registry.add_provider(provider)
    return {"status": "created", "provider": result.name}


@router.get("/providers/{name}")
async def get_provider(name: str):
    provider = await registry.get_provider(name)
    if not provider:
        raise HTTPException(status_code=404, detail=f"Provider '{name}' not found")
    return {
        "name": provider.name,
        "provider_type": provider.provider_type,
        "is_enabled": provider.is_enabled,
        "priority": provider.priority,
        "base_url": provider.base_url,
        "api_key": provider.api_key,
        "default_model": provider.default_model,
        "config": provider.config,
    }


@router.delete("/providers/{name}")
async def delete_provider(name: str):
    success = await registry.remove_provider(name)
    if not success:
        raise HTTPException(status_code=404, detail=f"Provider '{name}' not found")
    return {"status": "deleted"}
