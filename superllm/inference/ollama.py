from __future__ import annotations

import asyncio
import time
from collections.abc import AsyncGenerator
from typing import Optional

import httpx

from superllm.config.settings import settings
from superllm.inference.base import (
    InferenceEngine,
    InferenceRequest,
    InferenceResponse,
    ModelInfo,
    ProviderHealth,
)


class OllamaInferenceEngine(InferenceEngine):
    """Adapter to talk to a local Ollama-like model server.

    Behavior:
    - Prefer a native `ollama` python package client if installed.
    - Otherwise use an HTTP endpoint (configurable `base_url`).

    Notes:
    - Ollama's HTTP API and python client have multiple revisions; adjust
      `base_url` and payload shape if your local server differs.
    """

    def __init__(self, base_url: Optional[str] = None, api_key: Optional[str] = None):
        self._client = None
        self._base_url = base_url or "http://localhost:11434"
        self._http: Optional[httpx.AsyncClient] = None
        self._api_key = api_key

    @property
    def name(self) -> str:
        return "ollama"

    async def _init_client(self):
        if self._client is not None or self._http is not None:
            return
        try:
            import ollama  # type: ignore

            self._client = ollama
        except Exception:
            # fallback to httpx async client
            headers = {"Authorization": f"Bearer {self._api_key}"} if self._api_key else {}
            self._http = httpx.AsyncClient(timeout=settings.cloud_request_timeout, headers=headers)

    async def _ensure_ready(self):
        await self._init_client()

    def _to_prompt(self, messages: list[dict]) -> str:
        # Flatten message list into a single prompt string compatible with many local servers
        parts = []
        for m in messages:
            role = m.get("role", "user")
            content = m.get("content", "")
            parts.append(f"[{role}] {content}")
        return "\n".join(parts)

    async def chat(self, request: InferenceRequest) -> InferenceResponse:
        await self._ensure_ready()
        start = time.time()
        resolved_model = request.model

        prompt = self._to_prompt(request.messages)

        try:
            if self._client is not None:
                # Using hypothetical ollama client API - check your installed client docs
                resp = self._client.run(model=resolved_model, prompt=prompt, max_tokens=request.max_tokens)
                content = getattr(resp, "text", str(resp))
            else:
                # HTTP fallback - many Ollama-compatible servers accept a POST to /run
                payload = {"model": resolved_model, "prompt": prompt, "max_tokens": request.max_tokens}
                r = await self._http.post(f"{self._base_url}/run", json=payload)
                r.raise_for_status()
                data = r.json()
                # try common fields
                content = data.get("output") or data.get("text") or data.get("result") or str(data)
        except Exception as e:
            raise RuntimeError(f"Ollama inference failed: {e}")

        elapsed = (time.time() - start) * 1000
        return InferenceResponse(
            model=request.model,
            content=content,
            finish_reason="stop",
            tokens_in=0,
            tokens_out=0,
            total_time_ms=elapsed,
        )

    async def chat_stream(self, request: InferenceRequest) -> AsyncGenerator[str, None]:
        await self._ensure_ready()
        resolved_model = request.model
        prompt = self._to_prompt(request.messages)

        if self._client is not None:
            # If client supports streaming, user should implement here.
            # For now, return single full response.
            resp = self._client.run(model=resolved_model, prompt=prompt, max_tokens=request.max_tokens)
            yield getattr(resp, "text", str(resp))
            return

        # HTTP streaming fallback (server must support chunked responses)
        headers = {"Authorization": f"Bearer {self._api_key}"} if self._api_key else {}
        async with httpx.AsyncClient(timeout=settings.cloud_request_timeout, headers=headers) as client:
            payload = {"model": resolved_model, "prompt": prompt, "max_tokens": request.max_tokens, "stream": True}
            try:
                async with client.stream("POST", f"{self._base_url}/run", json=payload, timeout=settings.cloud_request_timeout) as r:
                    r.raise_for_status()
                    async for chunk in r.aiter_text():
                        if chunk:
                            yield chunk
            except Exception as e:
                raise RuntimeError(f"Ollama streaming failed: {e}")

    async def list_models(self) -> list[ModelInfo]:
        await self._ensure_ready()
        if self._client is not None:
            try:
                models = self._client.models()
                return [ModelInfo(id=m["name"]) for m in models]
            except Exception:
                return []
        try:
            headers = {"Authorization": f"Bearer {self._api_key}"} if self._api_key else {}
            async with httpx.AsyncClient(timeout=10, headers=headers) as client:
                r = await client.get(f"{self._base_url}/models")
                r.raise_for_status()
                data = r.json()
                return [ModelInfo(id=m.get("name") or m.get("id")) for m in data]
        except Exception:
            return []

    async def health(self) -> ProviderHealth:
        start = time.time()
        try:
            await self._ensure_ready()
            latency = (time.time() - start) * 1000
            return ProviderHealth(name="ollama", healthy=True, latency_ms=latency)
        except Exception as e:
            latency = (time.time() - start) * 1000
            return ProviderHealth(name="ollama", healthy=False, latency_ms=latency, error=str(e))

    async def close(self):
        if self._http is not None:
            await self._http.aclose()
            self._http = None
