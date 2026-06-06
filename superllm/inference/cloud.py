from __future__ import annotations

import time
from typing import AsyncGenerator, Optional

from superllm.config.settings import settings
from superllm.inference.base import (
    InferenceEngine,
    InferenceRequest,
    InferenceResponse,
    ModelInfo,
    ProviderHealth,
)


class CloudInferenceEngine(InferenceEngine):
    def __init__(self):
        self._client = None

    @property
    def name(self) -> str:
        return "cloud"

    async def _init_client(self):
        if self._client is not None:
            return
        try:
            import litellm
            self._client = litellm
        except ImportError:
            raise RuntimeError(
                "litellm not installed. Run: pip install 'superllm[cloud]'"
            )

    async def chat(self, request: InferenceRequest) -> InferenceResponse:
        await self._init_client()
        start = time.time()

        try:
            response = await self._client.acompletion(
                model=request.model,
                messages=request.messages,
                temperature=request.temperature,
                max_tokens=request.max_tokens,
                top_p=request.top_p,
                stop=request.stop,
                presence_penalty=request.presence_penalty,
                frequency_penalty=request.frequency_penalty,
                timeout=settings.cloud_request_timeout,
            )
        except Exception as e:
            raise RuntimeError(f"Cloud inference failed: {e}")

        elapsed = (time.time() - start) * 1000
        choice = response.choices[0]
        usage = getattr(response, "usage", {})

        return InferenceResponse(
            model=request.model,
            content=choice.message.content or "",
            finish_reason=choice.finish_reason or "stop",
            tokens_in=getattr(usage, "prompt_tokens", 0),
            tokens_out=getattr(usage, "completion_tokens", 0),
            total_time_ms=elapsed,
        )

    async def chat_stream(
        self, request: InferenceRequest
    ) -> AsyncGenerator[str, None]:
        await self._init_client()

        try:
            response = await self._client.acompletion(
                model=request.model,
                messages=request.messages,
                temperature=request.temperature,
                max_tokens=request.max_tokens,
                top_p=request.top_p,
                stop=request.stop,
                presence_penalty=request.presence_penalty,
                frequency_penalty=request.frequency_penalty,
                stream=True,
                timeout=settings.cloud_request_timeout,
            )
        except Exception as e:
            raise RuntimeError(f"Cloud streaming failed: {e}")

        async for chunk in response:
            delta = chunk.choices[0].delta if chunk.choices else None
            if delta and delta.content:
                yield delta.content

    async def list_models(self) -> list[ModelInfo]:
        await self._init_client()
        try:
            models = await self._client.amodel_list()
            return [ModelInfo(id=m.id, owned_by=m.owned_by) for m in models.data]
        except Exception:
            return []

    async def health(self) -> ProviderHealth:
        start = time.time()
        try:
            await self._init_client()
            latency = (time.time() - start) * 1000
            return ProviderHealth(name="cloud", healthy=True, latency_ms=latency)
        except Exception as e:
            latency = (time.time() - start) * 1000
            return ProviderHealth(name="cloud", healthy=False, latency_ms=latency, error=str(e))

    async def close(self):
        self._client = None
