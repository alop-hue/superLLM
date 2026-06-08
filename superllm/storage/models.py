from __future__ import annotations

import datetime

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy import (
    Enum as SAEnum,
)
from sqlalchemy.orm import relationship

from superllm.config.settings import ProviderType
from superllm.storage.db import Base


class InstalledModel(Base):
    __tablename__ = "installed_models"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), unique=True, nullable=False, index=True)
    display_name = Column(String(255))
    path = Column(Text, nullable=False)
    model_type = Column(String(50), default="gguf")
    architecture = Column(String(100))
    parameter_count = Column(String(50))
    context_length = Column(Integer, default=2048)
    size_bytes = Column(Integer, default=0)
    sha256 = Column(String(64))
    quant = Column(String(20))
    tags = Column(JSON, default=list)
    capabilities = Column(JSON, default=dict)
    metadata_json = Column(JSON, default=dict)
    is_pinned = Column(Boolean, default=False)
    download_date = Column(DateTime, default=datetime.datetime.utcnow)
    last_used = Column(DateTime, nullable=True)
    use_count = Column(Integer, default=0)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "display_name": self.display_name or self.name,
            "path": self.path,
            "model_type": self.model_type,
            "architecture": self.architecture,
            "parameter_count": self.parameter_count,
            "context_length": self.context_length,
            "size_bytes": self.size_bytes,
            "size_display": self._format_size(self.size_bytes),
            "sha256": self.sha256,
            "quant": self.quant,
            "tags": self.tags or [],
            "capabilities": self.capabilities or {},
            "is_pinned": self.is_pinned,
            "download_date": self.download_date.isoformat() if self.download_date else None,
            "last_used": self.last_used.isoformat() if self.last_used else None,
            "use_count": self.use_count,
        }

    @staticmethod
    def _format_size(size_bytes: int) -> str:
        if size_bytes < 1024:
            return f"{size_bytes} B"
        if size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        if size_bytes < 1024 * 1024 * 1024:
            return f"{size_bytes / (1024 * 1024):.1f} MB"
        return f"{size_bytes / (1024 * 1024 * 1024):.2f} GB"


class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(255), default="New Chat")
    model = Column(String(255))
    provider = Column(String(50), default="local")
    mode = Column(String(10), default="local")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(
        DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow
    )
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "model": self.model,
            "provider": self.provider,
            "mode": self.mode,
            "message_count": len(self.messages)
            if hasattr(self, "messages") and self.messages is not None
            else 0,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    conversation_id = Column(
        Integer, ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False
    )
    role = Column(String(20), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    tokens_in = Column(Integer, nullable=True)
    tokens_out = Column(Integer, nullable=True)
    metadata_json = Column(JSON, default=dict)

    conversation = relationship("Conversation", back_populates="messages")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "conversation_id": self.conversation_id,
            "role": self.role,
            "content": self.content,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "tokens_in": self.tokens_in,
            "tokens_out": self.tokens_out,
        }


class ProviderConfig(Base):
    __tablename__ = "provider_configs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False)
    provider_type = Column(SAEnum(ProviderType), nullable=False)
    api_key = Column(Text, nullable=True)
    base_url = Column(String(500), nullable=True)
    default_model = Column(String(255))
    is_enabled = Column(Boolean, default=True)
    priority = Column(Integer, default=0)
    config_json = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "provider_type": self.provider_type.value if self.provider_type else None,
            "base_url": self.base_url,
            "default_model": self.default_model,
            "is_enabled": self.is_enabled,
            "priority": self.priority,
            "config": self.config_json or {},
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class Setting(Base):
    __tablename__ = "settings"

    key = Column(String(255), primary_key=True)
    value = Column(Text, nullable=True)
    updated_at = Column(
        DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow
    )
