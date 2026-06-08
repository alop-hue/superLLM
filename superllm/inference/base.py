from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import AsyncGenerator
from dataclasses import dataclass, field


@dataclass
class InferenceRequest:
    model: str
    messages: list[dict]
    stream: bool = False
    temperature: float = 0.7
    max_tokens: int | None = None
    top_p: float = 0.95
    top_k: int = 40
    stop: list[str] | None = None
    presence_penalty: float = 0.0
    frequency_penalty: float = 0.0
    metadata: dict = field(default_factory=dict)


@dataclass
class InferenceResponse:
    model: str
    content: str
    finish_reason: str = "stop"
    tokens_in: int = 0
    tokens_out: int = 0
    total_time_ms: float = 0.0


@dataclass
class ModelInfo:
    id: str
    object: str = "model"
    owned_by: str = "superllm"
    permissions: list = field(default_factory=list)


@dataclass
class ProviderHealth:
    name: str
    healthy: bool
    latency_ms: float
    error: str | None = None


class InferenceEngine(ABC):
    @abstractmethod
    async def chat(self, request: InferenceRequest) -> InferenceResponse: ...

    @abstractmethod
    def chat_stream(self, request: InferenceRequest) -> AsyncGenerator[str, None]: ...

    @abstractmethod
    async def list_models(self) -> list[ModelInfo]: ...

    @abstractmethod
    async def health(self) -> ProviderHealth: ...

    @abstractmethod
    async def close(self): ...

    @property
    @abstractmethod
    def name(self) -> str: ...
