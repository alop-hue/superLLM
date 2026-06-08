from __future__ import annotations

import time
from collections.abc import AsyncGenerator

from superllm.config.settings import settings
from superllm.inference.base import (
    InferenceEngine,
    InferenceRequest,
    InferenceResponse,
    ModelInfo,
    ProviderHealth,
)


class LocalInferenceEngine(InferenceEngine):
    def __init__(self):
        self._model = None
        self._current_model_path: str | None = None
        self._loaded = False

    @property
    def name(self) -> str:
        return "local"

    async def _load_model(self, model_path: str):
        if self._current_model_path == model_path and self._loaded:
            return
        self._current_model_path = model_path
        self._loaded = False

        try:
            from llama_cpp import Llama
            self._model = Llama(
                model_path=model_path,
                n_ctx=settings.local_n_ctx,
                n_gpu_layers=settings.local_n_gpu_layers,
                n_threads=settings.local_n_threads or None,
                verbose=settings.local_verbose,
            )
            self._loaded = True
        except ImportError:
            raise RuntimeError(
                "llama-cpp-python not installed. Run: .venv/bin/pip install 'superllm[local]' (or activate venv: source .venv/bin/activate)"
            )
        except Exception as e:
            raise RuntimeError(f"Failed to load model: {e}")

    async def _ensure_loaded(self, request: InferenceRequest):
        if self._loaded and self._model:
            return
        from superllm.models.registry import ModelRegistry
        registry = ModelRegistry.get_instance()
        installed = await registry.get_model(request.model)
        if installed and installed.path:
            await self._load_model(installed.path)
        else:
            raise RuntimeError(
                f"Model '{request.model}' is not installed locally. "
                f"Run 'superllm pull {request.model}' to download it first."
            )

    async def chat(self, request: InferenceRequest) -> InferenceResponse:
        await self._ensure_loaded(request)

        start = time.time()
        response = self._model.create_chat_completion(
            messages=request.messages,
            temperature=request.temperature,
            max_tokens=request.max_tokens or settings.local_max_tokens,
            top_p=request.top_p,
            stop=request.stop,
            presence_penalty=request.presence_penalty,
            frequency_penalty=request.frequency_penalty,
        )
        elapsed = (time.time() - start) * 1000

        choice = response.get("choices", [{}])[0]
        content = choice.get("message", {}).get("content", "")
        finish = choice.get("finish_reason", "stop")
        usage = response.get("usage", {})

        return InferenceResponse(
            model=request.model,
            content=content,
            finish_reason=finish,
            tokens_in=usage.get("prompt_tokens", 0),
            tokens_out=usage.get("completion_tokens", 0),
            total_time_ms=elapsed,
        )

    async def chat_stream(
        self, request: InferenceRequest
    ) -> AsyncGenerator[str, None]:
        await self._ensure_loaded(request)

        stream = self._model.create_chat_completion(
            messages=request.messages,
            temperature=request.temperature,
            max_tokens=request.max_tokens or settings.local_max_tokens,
            top_p=request.top_p,
            stop=request.stop,
            presence_penalty=request.presence_penalty,
            frequency_penalty=request.frequency_penalty,
            stream=True,
        )

        for chunk in stream:
            choice = chunk.get("choices", [{}])[0]
            delta = choice.get("delta", {})
            content = delta.get("content", "")
            if content:
                yield content

    async def list_models(self) -> list[ModelInfo]:
        from superllm.models.registry import ModelRegistry
        registry = ModelRegistry.get_instance()
        models = await registry.list_installed()
        return [ModelInfo(id=m.name) for m in models]

    async def health(self) -> ProviderHealth:
        start = time.time()
        try:
            if self._loaded and self._model:
                latency = (time.time() - start) * 1000
                return ProviderHealth(name="local", healthy=True, latency_ms=latency)
            return ProviderHealth(name="local", healthy=False, latency_ms=0, error="No model loaded")
        except Exception as e:
            latency = (time.time() - start) * 1000
            return ProviderHealth(name="local", healthy=False, latency_ms=latency, error=str(e))

    async def close(self):
        if self._model is not None:
            self._model.close()
            self._model = None
            self._loaded = False
