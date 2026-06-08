from __future__ import annotations

import contextlib
from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from superllm.config.settings import settings


class Base(DeclarativeBase):
    pass


class Database:
    _instance: Database | None = None

    def __init__(self, database_url: str | None = None):
        self.database_url = database_url or settings.database_url
        self._engine: AsyncEngine | None = None
        self._session_factory: async_sessionmaker[AsyncSession] | None = None

    @classmethod
    def get_instance(cls, database_url: str | None = None) -> Database:
        if cls._instance is None:
            cls._instance = cls(database_url)
        return cls._instance

    async def connect(self):
        if self._engine is not None:
            return
        self._engine = create_async_engine(
            self.database_url,
            echo=settings.debug,
            future=True,
        )
        self._session_factory = async_sessionmaker(
            self._engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )

    async def disconnect(self):
        if self._engine is not None:
            await self._engine.dispose()
            self._engine = None
            self._session_factory = None

    async def create_all(self):
        if self._engine is None:
            await self.connect()
        async with self._engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    @contextlib.asynccontextmanager
    async def session(self) -> AsyncGenerator[AsyncSession, None]:
        if self._session_factory is None:
            await self.connect()
        async with self._session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()

    @property
    def engine(self) -> AsyncEngine:
        if self._engine is None:
            raise RuntimeError("Database not connected. Call connect() first.")
        return self._engine
