from __future__ import annotations

import asyncio
import time
from typing import AsyncGenerator, Optional

from superllm.config.settings import Mode, settings
from superllm.inference.base import (
    InferenceEngine,
    InferenceRequest,
    InferenceResponse,
    ModelInfo,
    ProviderHealth,
)
from superllm.inference.local import LocalInferenceEngine
from superllm.inference.cloud import CloudInferenceEngine


class RoutingStrategy:
    auto = "auto"
    local_first = "local_first"
    cloud_first = "cloud_first"
    local_only = "local_only"
    cloud_only = "cloud_only"
    cheapest = "cheapest"
    fastest = "fastest"


class InferenceRouter(InferenceEngine):
    def __init__(self):
        self._local: Optional[LocalInferenceEngine] = None
        self._cloud: Optional[CloudInferenceEngine] = None
        self._strategy: str = RoutingStrategy.auto

    @property
    def name(self) -> str:
        return "router"

    def set_strategy(self, strategy: str):
        if strategy not in (
            RoutingStrategy.auto,
            RoutingStrategy.local_first,
            RoutingStrategy.cloud_first,
            RoutingStrategy.local_only,
            RoutingStrategy.cloud_only,
            RoutingStrategy.cheapest,
            RoutingStrategy.fastest,
        ):
            raise ValueError(f"Unknown strategy: {strategy}")
        self._strategy = strategy

    async def _get_local(self) -> LocalInferenceEngine:
        if self._local is None:
            self._local = LocalInferenceEngine()
        return self._local

    async def _get_cloud(self) -> CloudInferenceEngine:
        if self._cloud is None:
            self._cloud = CloudInferenceEngine()
        return self._cloud

    async def _resolve_engine(self) -> tuple[InferenceEngine, str]:
        mode = settings.mode
        strategy = self._strategy

        if mode == Mode.local:
            return await self._get_local(), "local"
        if mode == Mode.cloud:
            return await self._get_cloud(), "cloud"

        if strategy == RoutingStrategy.local_only:
            return await self._get_local(), "local"
        if strategy == RoutingStrategy.cloud_only:
            return await self._get_cloud(), "cloud"
        if strategy == RoutingStrategy.cloud_first:
            return await self._get_cloud(), "cloud"

        return await self._get_local(), "local"

    async def chat(self, request: InferenceRequest) -> InferenceResponse:
        engine, provider = await self._resolve_engine()
        try:
            return await engine.chat(request)
        except Exception as local_err:
            if settings.cloud_fallback and provider == "local":
                try:
                    cloud = await self._get_cloud()
                    return await cloud.chat(request)
                except Exception as cloud_err:
                    raise RuntimeError(
                        f"Local failed: {local_err}; Cloud fallback failed: {cloud_err}"
                    )
            raise

    async def chat_stream(
        self, request: InferenceRequest
    ) -> AsyncGenerator[str, None]:
        engine, provider = await self._resolve_engine()
        try:
            async for chunk in engine.chat_stream(request):
                yield chunk
        except Exception as local_err:
            if settings.cloud_fallback and provider == "local":
                try:
                    cloud = await self._get_cloud()
                    async for chunk in cloud.chat_stream(request):
                        yield chunk
                except Exception as cloud_err:
                    raise RuntimeError(
                        f"Local stream failed: {local_err}; Cloud fallback failed: {cloud_err}"
                    )
            raise

    async def list_models(self) -> list[ModelInfo]:
        local_models = []
        cloud_models = []

        if settings.mode in (Mode.local, Mode.hybrid):
            try:
                engine = await self._get_local()
                local_models = await engine.list_models()
            except Exception:
                pass

        if settings.mode in (Mode.cloud, Mode.hybrid):
            try:
                engine = await self._get_cloud()
                cloud_models = await engine.list_models()
            except Exception:
                pass

        return local_models + cloud_models

    async def health(self) -> ProviderHealth:
        start = time.time()
        try:
            engine, _ = await self._resolve_engine()
            return await engine.health()
        except Exception as e:
            return ProviderHealth(
                name="router",
                healthy=False,
                latency_ms=(time.time() - start) * 1000,
                error=str(e),
            )

    async def close(self):
        if self._local:
            await self._local.close()
        if self._cloud:
            await self._cloud.close()
