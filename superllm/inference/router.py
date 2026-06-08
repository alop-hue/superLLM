from __future__ import annotations

import time
from collections.abc import AsyncGenerator

from superllm.config.settings import Mode, settings
from superllm.inference.base import (
    InferenceEngine,
    InferenceRequest,
    InferenceResponse,
    ModelInfo,
    ProviderHealth,
)
from superllm.inference.cloud import CloudInferenceEngine
from superllm.inference.local import LocalInferenceEngine
from superllm.models.library import LITELLM_MODEL_MAP
from superllm.inference.ollama import OllamaInferenceEngine
from superllm.inference.openclaw import OpenClawInferenceEngine
from superllm.inference.opencode import OpenCodeInferenceEngine


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
        self._local: LocalInferenceEngine | None = None
        self._cloud: CloudInferenceEngine | None = None
        self._ollama_instances: dict[str, OllamaInferenceEngine] = {}
        self._openclaw_instances: dict[str, OpenClawInferenceEngine] = {}
        self._opencode_instances: dict[str, OpenCodeInferenceEngine] = {}
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

    async def _get_ollama(self, base_url: str | None = None, api_key: str | None = None) -> OllamaInferenceEngine:
        key = f"{base_url or 'default'}|{api_key or ''}"
        if key not in self._ollama_instances:
            self._ollama_instances[key] = OllamaInferenceEngine(base_url=base_url, api_key=api_key)
        return self._ollama_instances[key]

    async def _get_openclaw(self, base_url: str | None = None, api_key: str | None = None) -> OpenClawInferenceEngine:
        key = f"{base_url or 'default'}|{api_key or ''}"
        if key not in self._openclaw_instances:
            self._openclaw_instances[key] = OpenClawInferenceEngine(base_url=base_url, api_key=api_key)
        return self._openclaw_instances[key]

    async def _get_opencode(self, base_url: str | None = None, api_key: str | None = None) -> OpenCodeInferenceEngine:
        key = f"{base_url or 'default'}|{api_key or ''}"
        if key not in self._opencode_instances:
            self._opencode_instances[key] = OpenCodeInferenceEngine(base_url=base_url, api_key=api_key)
        return self._opencode_instances[key]

    async def _resolve_engine_and_model(self, model_name: str) -> tuple[InferenceEngine, str, str]:
        mode = settings.mode
        strategy = self._strategy
        is_cloud_model = ":cloud" in model_name or self._is_cloud_native(model_name)
        is_ollama_model = ":ollama" in model_name
        is_openclaw_model = ":openclaw" in model_name
        is_opencode_model = ":opencode" in model_name
        engine_type = "local"

        # If the name explicitly targets a specific provider-backed model via suffix
        if is_ollama_model:
            engine_type = "ollama"
        elif is_openclaw_model:
            engine_type = "openclaw"
        elif is_opencode_model:
            engine_type = "opencode"
        elif mode == Mode.cloud or strategy == RoutingStrategy.cloud_only or is_cloud_model:
            engine_type = "cloud"
        elif strategy == RoutingStrategy.local_only:
            engine_type = "local"
        elif strategy == RoutingStrategy.cloud_first:
            engine_type = "cloud"

        if engine_type == "cloud":
            resolved = self._resolve_cloud_model(model_name)
            cloud = await self._get_cloud()
            return cloud, resolved, "cloud"

        if engine_type == "ollama":
            # strip possible suffix and resolve simple model name
            resolved = model_name.replace(":ollama", "")
            # prefer a DB-registered provider for ollama if available
            from superllm.providers.registry import registry

            provider = None
            try:
                providers = await registry.get_providers()
                for p in providers:
                    if p.provider_type == "ollama" and p.is_enabled:
                        provider = p
                        break
            except Exception:
                provider = None

            if provider:
                oll = await self._get_ollama(provider.base_url, getattr(provider, "api_key", None))
            else:
                oll = await self._get_ollama()
            return oll, resolved, "ollama"

        if engine_type == "openclaw":
            resolved = model_name.replace(":openclaw", "")
            from superllm.providers.registry import registry

            provider = None
            try:
                providers = await registry.get_providers()
                for p in providers:
                    if p.provider_type == "openclaw" and p.is_enabled:
                        provider = p
                        break
            except Exception:
                provider = None

            if provider:
                oc = await self._get_openclaw(provider.base_url, getattr(provider, "api_key", None))
            else:
                oc = await self._get_openclaw()
            return oc, resolved, "openclaw"

        if engine_type == "opencode":
            resolved = model_name.replace(":opencode", "")
            from superllm.providers.registry import registry

            provider = None
            try:
                providers = await registry.get_providers()
                for p in providers:
                    if p.provider_type == "opencode" and p.is_enabled:
                        provider = p
                        break
            except Exception:
                provider = None

            if provider:
                oe = await self._get_opencode(provider.base_url, getattr(provider, "api_key", None))
            else:
                oe = await self._get_opencode()
            return oe, resolved, "opencode"

        engine = await self._get_local()
        resolved_path = await self._resolve_local_model(model_name)
        if resolved_path:
            await engine._load_model(resolved_path)
        return engine, model_name, "local"

    def _is_cloud_native(self, model_name: str) -> bool:
        from superllm.models.library import ModelLibrary
        card = ModelLibrary.get_model(model_name)
        if card and card.source == "cloud":
            return True
        return model_name in LITELLM_MODEL_MAP

    def _resolve_cloud_model(self, model_name: str) -> str:
        if model_name in LITELLM_MODEL_MAP:
            return LITELLM_MODEL_MAP[model_name]
        base = model_name.replace(":cloud", "").replace(":local", "")
        if base in LITELLM_MODEL_MAP:
            return LITELLM_MODEL_MAP[base]
        return self._default_cloud_for(model_name)

    def _default_cloud_for(self, model_name: str) -> str:
        from superllm.models.library import ModelLibrary
        card = ModelLibrary.get_model(model_name)
        if card:
            for tag in card.tags:
                cloud_tag = f"{card.architecture}-{tag}:cloud"
                if cloud_tag in LITELLM_MODEL_MAP:
                    return LITELLM_MODEL_MAP[cloud_tag]
        strategy = {
            "qwen": "together_ai/Qwen/Qwen2.5-72B-Instruct-Turbo",
            "llama": "together_ai/meta-llama/Meta-Llama-3.1-405B-Instruct-Turbo",
            "deepseek": "together_ai/deepseek-ai/DeepSeek-V3-0324",
            "mistral": "mistral/mistral-large-latest",
        }
        for key, mapped in strategy.items():
            if key in model_name.lower():
                return mapped
        return "together_ai/Qwen/Qwen2.5-72B-Instruct-Turbo"

    async def _resolve_local_model(self, model_name: str) -> str | None:
        from superllm.models.registry import ModelRegistry
        registry = ModelRegistry.get_instance()
        installed = await registry.get_model(model_name)
        if installed:
            return installed.path
        return None

    def _build_error_hint(self, model_name: str, local_err: Exception) -> str:
        from superllm.models.library import ModelLibrary
        card = ModelLibrary.get_model(model_name)
        hint = f"Model '{model_name}' is not available locally.\n"
        if card and card.source == "cloud":
            hint += f"  → This is a cloud model. Use --cloud flag or add :cloud suffix.\n"
        elif card:
            hint += f"  → Run 'superllm pull {model_name}' to download it.\n"
            alt = self._resolve_cloud_model(model_name)
            if alt != model_name:
                hint += f"  → Or use cloud fallback with: {alt}\n"
        else:
            hint += f"  → Run 'superllm library' to find available models.\n"
        return f"{local_err}\n{hint}"

    async def chat(self, request: InferenceRequest) -> InferenceResponse:
        engine, resolved_model, provider = await self._resolve_engine_and_model(request.model)
        request.model = resolved_model
        try:
            return await engine.chat(request)
        except Exception as local_err:
            if settings.cloud_fallback and provider == "local":
                try:
                    cloud = await self._get_cloud()
                    request.model = self._resolve_cloud_model(request.model)
                    return await cloud.chat(request)
                except Exception as cloud_err:
                    raise RuntimeError(
                        f"{self._build_error_hint(request.model, local_err)}Cloud fallback failed: {cloud_err}"
                    )
            raise

    async def chat_stream(
        self, request: InferenceRequest
    ) -> AsyncGenerator[str, None]:
        engine, resolved_model, provider = await self._resolve_engine_and_model(request.model)
        request.model = resolved_model
        try:
            async for chunk in engine.chat_stream(request):
                yield chunk
        except Exception as local_err:
            if settings.cloud_fallback and provider == "local":
                try:
                    cloud = await self._get_cloud()
                    request.model = self._resolve_cloud_model(request.model)
                    async for chunk in cloud.chat_stream(request):
                        yield chunk
                except Exception as cloud_err:
                    raise RuntimeError(
                        f"{self._build_error_hint(request.model, local_err)}Cloud fallback failed: {cloud_err}"
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
            engine, _, _ = await self._resolve_engine_and_model("")
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
