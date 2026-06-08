from __future__ import annotations

from typing import Optional

from sqlalchemy import select

from superllm.config.settings import ProviderType
from superllm.providers.base import Provider, ProviderRegistry
from superllm.storage.db import Database
from superllm.storage.models import ProviderConfig as ProviderConfigModel


class DBProviderRegistry(ProviderRegistry):
    def __init__(self, database: Optional[Database] = None):
        self._db = database or Database.get_instance()

    async def get_providers(self) -> list[Provider]:
        async with self._db.session() as session:
            result = await session.execute(
                select(ProviderConfigModel).order_by(ProviderConfigModel.priority)
            )
            configs = result.scalars().all()
            return [self._to_provider(c) for c in configs]

    async def get_provider(self, name: str) -> Optional[Provider]:
        async with self._db.session() as session:
            result = await session.execute(
                select(ProviderConfigModel).where(ProviderConfigModel.name == name)
            )
            config = result.scalar_one_or_none()
            return self._to_provider(config) if config else None

    async def add_provider(self, provider: Provider) -> Provider:
        async with self._db.session() as session:
            config = ProviderConfigModel(
                name=provider.name,
                provider_type=ProviderType(provider.provider_type),
                api_key=provider.api_key,
                base_url=provider.base_url,
                default_model=provider.default_model,
                is_enabled=provider.is_enabled,
                priority=provider.priority,
                config_json=provider.config,
            )
            session.add(config)
            await session.flush()
            return self._to_provider(config)

    async def remove_provider(self, name: str) -> bool:
        async with self._db.session() as session:
            result = await session.execute(
                select(ProviderConfigModel).where(ProviderConfigModel.name == name)
            )
            config = result.scalar_one_or_none()
            if not config:
                return False
            await session.delete(config)
            return True

    async def update_provider(self, provider: Provider) -> Optional[Provider]:
        async with self._db.session() as session:
            result = await session.execute(
                select(ProviderConfigModel).where(ProviderConfigModel.name == provider.name)
            )
            config = result.scalar_one_or_none()
            if not config:
                return None
            config.provider_type = ProviderType(provider.provider_type)
            config.api_key = provider.api_key
            config.base_url = provider.base_url
            config.default_model = provider.default_model
            config.is_enabled = provider.is_enabled
            config.priority = provider.priority
            config.config_json = provider.config
            await session.flush()
            return self._to_provider(config)

    @staticmethod
    def _to_provider(config: ProviderConfigModel) -> Provider:
        return Provider(
            name=config.name,
            provider_type=config.provider_type.value if config.provider_type else "local",
            api_key=config.api_key,
            base_url=config.base_url,
            default_model=config.default_model,
            is_enabled=config.is_enabled,
            priority=config.priority,
            config=config.config_json or {},
        )


registry: ProviderRegistry = DBProviderRegistry()
