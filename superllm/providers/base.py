from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass
class Provider:
    name: str
    provider_type: str
    is_enabled: bool = True
    priority: int = 0
    base_url: str | None = None
    default_model: str | None = None
    api_key: str | None = None
    config: dict = field(default_factory=dict)
    health_status: bool | None = None


class ProviderRegistry(ABC):
    @abstractmethod
    async def get_providers(self) -> list[Provider]: ...

    @abstractmethod
    async def get_provider(self, name: str) -> Provider | None: ...

    @abstractmethod
    async def add_provider(self, provider: Provider) -> Provider: ...

    @abstractmethod
    async def remove_provider(self, name: str) -> bool: ...

    @abstractmethod
    async def update_provider(self, provider: Provider) -> Provider | None: ...
