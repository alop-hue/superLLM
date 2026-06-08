from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from superllm.config.settings import settings
from superllm.models.library import ModelLibrary
from superllm.models.registry import ModelRegistry

router = APIRouter()
registry = ModelRegistry.get_instance()


class PullRequest(BaseModel):
    name: str
    quantization: str = "Q4_K_M"


class PullResponse(BaseModel):
    name: str
    status: str
    message: str
    path: Optional[str] = None


@router.get("/tags")
@router.get("/models")
async def list_models():
    models = await registry.list_installed()
    return {
        "models": [m.to_dict() for m in models],
        "total": len(models),
    }


@router.get("/models/library")
async def list_library(
    query: str = "",
    category: Optional[str] = None,
    tag: Optional[str] = None,
):
    if query or category or tag:
        tags = [tag] if tag else None
        results = ModelLibrary.filter(category=category, tags=tags)
        if query:
            results = [m for m in results if query.lower() in m.name.lower() or query.lower() in m.display_name.lower()]
    else:
        results = ModelLibrary.search()
    return {
        "models": [
            {
                "name": m.name,
                "display_name": m.display_name,
                "description": m.description,
                "architecture": m.architecture,
                "parameter_count": m.parameter_count,
                "context_length": m.context_length,
                "quantizations": m.quantizations,
                "tags": m.tags,
                "capabilities": m.capabilities,
                "category": m.category,
                "recommended_ram": m.recommended_ram,
                "size_estimates": m.size_estimates,
                "latency_profile": m.latency_profile,
                "strengths": m.strengths,
                "weaknesses": m.weaknesses,
                "model_family": m.model_family,
            }
            for m in results
        ],
        "total": len(results),
    }


@router.get("/models/search")
async def search_models(query: str = ""):
    results = ModelLibrary.search(query)
    return {
        "results": [
            {
                "name": m.name,
                "display_name": m.display_name,
                "description": m.description,
                "parameter_count": m.parameter_count,
                "context_length": m.context_length,
                "quantizations": m.quantizations,
                "tags": m.tags,
                "category": m.category,
                "capabilities": m.capabilities,
                "recommended_ram": m.recommended_ram,
                "size_estimates": m.size_estimates,
            }
            for m in results
        ],
        "total": len(results),
        "query": query,
    }


@router.get("/models/categories")
async def list_categories():
    return {
        "categories": ModelLibrary.categories(),
        "tags": ModelLibrary.all_tags(),
    }


@router.get("/models/recommend")
async def recommend_models(
    task: str = "chat",
    max_ram: float = 32.0,
    category: Optional[str] = None,
):
    if task == "hardware":
        results = ModelLibrary.recommend_for_hardware(max_ram)
    elif task == "all":
        results = ModelLibrary.recommend_for_hardware(max_ram)
    else:
        results = ModelLibrary.recommend_for_task(task, max_ram)
    if category:
        results = [m for m in results if m.category == category]
    return {
        "models": [
            {
                "name": m.name,
                "display_name": m.display_name,
                "category": m.category,
                "latency_profile": m.latency_profile,
                "recommended_ram": m.recommended_ram,
                "capabilities": m.capabilities,
                "strengths": m.strengths,
                "tags": m.tags,
            }
            for m in results[:50]
        ],
        "total": len(results),
        "task": task,
        "max_ram_gb": max_ram,
    }


@router.get("/models/summarize")
async def library_summary():
    return ModelLibrary.summarize()


@router.get("/models/{name}")
async def get_model(name: str):
    model = await registry.get_model(name)
    if not model:
        raise HTTPException(status_code=404, detail=f"Model '{name}' not found")
    card = ModelLibrary.get_model(name)
    result = model.to_dict()
    if card:
        result["library_info"] = {
            "description": card.description,
            "category": card.category,
            "recommended_ram": card.recommended_ram,
            "quantizations": card.quantizations,
            "url": card.url,
            "latency_profile": card.latency_profile,
            "strengths": card.strengths,
            "weaknesses": card.weaknesses,
            "model_family": card.model_family,
        }
    return result


@router.post("/pull")
async def pull_model(request: PullRequest):
    name = request.name
    card = ModelLibrary.get_model(name)
    if not card:
        raise HTTPException(status_code=404, detail=f"Model '{name}' not found in library")

    quant = request.quantization
    download_url = card.url or ModelLibrary.resolve_download_url(name, quant)
    if not download_url:
        raise HTTPException(status_code=400, detail=f"No download URL for model '{name}'")

    import httpx
    filename = f"{name.replace('.', '-')}-{quant}.gguf"
    models_dir = settings.models_dir
    models_dir.mkdir(parents=True, exist_ok=True)
    dest_path = models_dir / filename

    if dest_path.exists():
        return PullResponse(
            name=name,
            status="exists",
            message=f"Model '{name}' already exists at {dest_path}",
            path=str(dest_path),
        )

    download_url = card.url or ModelLibrary.resolve_download_url(name, quant)
    if not download_url:
        raise HTTPException(status_code=400, detail=f"Cannot resolve download URL for '{name}'")

    try:
        async with httpx.AsyncClient(timeout=settings.model_pull_timeout, follow_redirects=True) as client:
            head = await client.head(download_url)
            if head.status_code >= 400:
                raise HTTPException(status_code=400, detail=f"Download URL returned {head.status_code}: {download_url}")
            response = await client.get(download_url)
            response.raise_for_status()
            content = response.content
            if len(content) < 1024:
                raise HTTPException(status_code=400, detail=f"Downloaded file is too small ({len(content)} bytes) - likely not a valid model file")
            dest_path.write_bytes(content)
    except HTTPException:
        raise
    except Exception as e:
        if dest_path.exists():
            dest_path.unlink()
        raise HTTPException(status_code=500, detail=f"Download failed: {e}")

    await registry.register_model(
        name=name,
        path=dest_path,
        architecture=card.architecture if card else None,
        parameter_count=card.parameter_count if card else None,
        context_length=card.context_length if card else 2048,
        quant=quant,
        tags=card.tags if card else [],
        capabilities=card.capabilities if card else {},
    )

    return PullResponse(
        name=name,
        status="downloaded",
        message=f"Successfully downloaded '{name}' ({quant})",
        path=str(dest_path),
    )


@router.delete("/models/{name}")
async def delete_model(name: str):
    success = await registry.remove_model(name)
    if not success:
        raise HTTPException(status_code=404, detail=f"Model '{name}' not found")
    return {"status": "deleted", "message": f"Model '{name}' deleted"}


# OpenAI-compatible /v1/models endpoint
@router.get("/v1/models")
@router.get("/v1/models/")
async def openai_list_models():
    installed = await registry.list_installed()
    library_models = ModelLibrary.search()
    all_models = []

    lib_names = {m.name for m in library_models}
    installed_names = {m.name for m in installed}

    for inst in installed:
        all_models.append({
            "id": inst.name,
            "object": "model",
            "created": int(inst.download_date.timestamp()) if inst.download_date else 0,
            "owned_by": "superllm",
            "capabilities": inst.capabilities or {},
        })

    for lib in library_models:
        if lib.name not in installed_names:
            all_models.append({
                "id": lib.name,
                "object": "model",
                "created": 0,
                "owned_by": "superllm",
                "capabilities": lib.capabilities,
            })

    return {
        "object": "list",
        "data": all_models,
    }
