from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from sqlalchemy import desc, select

from superllm.storage.db import Database
from superllm.storage.models import Conversation, Message

router = APIRouter()
db = Database.get_instance()


class ConversationCreate(BaseModel):
    title: str = "New Chat"
    model: str = "default"
    provider: str = "local"
    mode: str = "local"


class MessageCreate(BaseModel):
    role: str
    content: str
    tokens_in: int | None = None
    tokens_out: int | None = None


@router.get("/conversations")
async def list_conversations(limit: int = 50, offset: int = 0):
    async with db.session() as session:
        result = await session.execute(
            select(Conversation).order_by(desc(Conversation.updated_at)).offset(offset).limit(limit)
        )
        convs = result.scalars().all()
        return {
            "conversations": [c.to_dict() for c in convs],
            "total": len(convs),
            "limit": limit,
            "offset": offset,
        }


@router.post("/conversations")
async def create_conversation(create: ConversationCreate):
    async with db.session() as session:
        conv = Conversation(
            title=create.title,
            model=create.model,
            provider=create.provider,
            mode=create.mode,
        )
        session.add(conv)
        await session.flush()
        return conv.to_dict()


@router.get("/conversations/{conv_id}")
async def get_conversation(conv_id: int):
    async with db.session() as session:
        result = await session.execute(select(Conversation).where(Conversation.id == conv_id))
        conv = result.scalar_one_or_none()
        if not conv:
            raise HTTPException(status_code=404, detail="Conversation not found")
        return conv.to_dict()


@router.delete("/conversations/{conv_id}")
async def delete_conversation(conv_id: int):
    async with db.session() as session:
        result = await session.execute(select(Conversation).where(Conversation.id == conv_id))
        conv = result.scalar_one_or_none()
        if not conv:
            raise HTTPException(status_code=404, detail="Conversation not found")
        await session.delete(conv)
        return {"status": "deleted"}


@router.get("/conversations/{conv_id}/messages")
async def list_messages(conv_id: int):
    async with db.session() as session:
        result = await session.execute(select(Conversation).where(Conversation.id == conv_id))
        conv = result.scalar_one_or_none()
        if not conv:
            raise HTTPException(status_code=404, detail="Conversation not found")

        msg_result = await session.execute(
            select(Message).where(Message.conversation_id == conv_id).order_by(Message.id)
        )
        messages = msg_result.scalars().all()
        return {"messages": [m.to_dict() for m in messages], "total": len(messages)}


@router.post("/conversations/{conv_id}/messages")
async def add_message(conv_id: int, msg: MessageCreate):
    async with db.session() as session:
        result = await session.execute(select(Conversation).where(Conversation.id == conv_id))
        conv = result.scalar_one_or_none()
        if not conv:
            raise HTTPException(status_code=404, detail="Conversation not found")

        message = Message(
            conversation_id=conv_id,
            role=msg.role,
            content=msg.content,
            tokens_in=msg.tokens_in,
            tokens_out=msg.tokens_out,
        )
        session.add(message)
        conv.updated_at = datetime.utcnow()
        await session.flush()
        return message.to_dict()
