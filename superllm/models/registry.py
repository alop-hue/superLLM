from __future__ import annotations

import hashlib
import shutil
from pathlib import Path
from typing import Optional

from sqlalchemy import select, func, delete as sa_delete

from superllm.config.settings import settings
from superllm.storage.db import Database
from superllm.storage.models import InstalledModel


class ModelRegistry:
    _instance: Optional[ModelRegistry] = None

    def __init__(self, database: Optional[Database] = None):
        self._db = database or Database.get_instance()

    @classmethod
    def get_instance(cls, database: Optional[Database] = None) -> ModelRegistry:
        if cls._instance is None:
            cls._instance = cls(database)
        return cls._instance

    async def list_installed(self) -> list[InstalledModel]:
        async with self._db.session() as session:
            result = await session.execute(
                select(InstalledModel).order_by(InstalledModel.name)
            )
            return list(result.scalars().all())

    async def get_model(self, name: str) -> Optional[InstalledModel]:
        async with self._db.session() as session:
            result = await session.execute(
                select(InstalledModel).where(InstalledModel.name == name)
            )
            return result.scalar_one_or_none()

    async def register_model(
        self,
        name: str,
        path: Path,
        model_type: str = "gguf",
        architecture: Optional[str] = None,
        parameter_count: Optional[str] = None,
        context_length: int = 2048,
        quant: Optional[str] = None,
        tags: Optional[list[str]] = None,
        capabilities: Optional[dict] = None,
    ) -> InstalledModel:
        size_bytes = path.stat().st_size if path.exists() else 0
        sha256 = self._compute_hash(path) if path.exists() else None

        async with self._db.session() as session:
            existing = await session.execute(
                select(InstalledModel).where(InstalledModel.name == name)
            )
            model = existing.scalar_one_or_none()
            if model:
                model.path = str(path)
                model.size_bytes = size_bytes
                model.sha256 = sha256
                model.architecture = architecture
                model.parameter_count = parameter_count
                model.context_length = context_length
                model.quant = quant
                if tags:
                    model.tags = tags
                if capabilities:
                    model.capabilities = capabilities
            else:
                model = InstalledModel(
                    name=name,
                    display_name=name,
                    path=str(path),
                    model_type=model_type,
                    architecture=architecture,
                    parameter_count=parameter_count,
                    context_length=context_length,
                    size_bytes=size_bytes,
                    sha256=sha256,
                    quant=quant,
                    tags=tags or [],
                    capabilities=capabilities or {},
                )
                session.add(model)
            await session.flush()
            return model

    async def remove_model(self, name: str) -> bool:
        async with self._db.session() as session:
            result = await session.execute(
                select(InstalledModel).where(InstalledModel.name == name)
            )
            model = result.scalar_one_or_none()
            if not model:
                return False
            path = Path(model.path)
            if path.exists():
                path.unlink()
            await session.delete(model)
            return True

    async def search_models(
        self,
        query: Optional[str] = None,
        tags: Optional[list[str]] = None,
        min_params: Optional[str] = None,
        max_params: Optional[str] = None,
    ) -> list[InstalledModel]:
        async with self._db.session() as session:
            stmt = select(InstalledModel)
            if query:
                stmt = stmt.where(
                    InstalledModel.name.ilike(f"%{query}%")
                )
            if tags:
                for tag in tags:
                    stmt = stmt.where(InstalledModel.tags.contains(tag))
            stmt = stmt.order_by(InstalledModel.name)
            result = await session.execute(stmt)
            return list(result.scalars().all())

    async def get_stats(self) -> dict:
        async with self._db.session() as session:
            count_result = await session.execute(
                select(func.count(InstalledModel.id))
            )
            total = count_result.scalar() or 0
            size_result = await session.execute(
                select(func.coalesce(func.sum(InstalledModel.size_bytes), 0))
            )
            total_size = size_result.scalar() or 0
            return {
                "total_models": total,
                "total_size_bytes": total_size,
                "total_size_display": self._format_size(total_size),
            }

    async def update_last_used(self, name: str):
        async with self._db.session() as session:
            result = await session.execute(
                select(InstalledModel).where(InstalledModel.name == name)
            )
            model = result.scalar_one_or_none()
            if model:
                import datetime
                model.last_used = datetime.datetime.utcnow()
                model.use_count = (model.use_count or 0) + 1

    @staticmethod
    def _compute_hash(path: Path) -> str:
        h = hashlib.sha256()
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                h.update(chunk)
        return h.hexdigest()

    @staticmethod
    def _format_size(size_bytes: int) -> str:
        if size_bytes < 1024:
            return f"{size_bytes} B"
        if size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        if size_bytes < 1024 * 1024 * 1024:
            return f"{size_bytes / (1024 * 1024):.1f} MB"
        return f"{size_bytes / (1024 * 1024 * 1024):.2f} GB"
