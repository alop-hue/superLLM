from __future__ import annotations

import json
import time
from typing import AsyncGenerator, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from sse_starlette.sse import EventSourceResponse

from superllm.inference.base import InferenceRequest
from superllm.inference.router import InferenceRouter

router = APIRouter()
_engine: Optional[InferenceRouter] = None


def get_engine():
    global _engine
    if _engine is None:
        _engine = InferenceRouter()
    return _engine


class FileAttachment(BaseModel):
    name: str
    type: str
    data: str
    size: int


class Message(BaseModel):
    role: str
    content: str
    files: Optional[list[FileAttachment]] = None


class ChatRequest(BaseModel):
    model: str
    messages: list[Message]
    stream: bool = False
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    top_p: float = 0.95
    top_k: int = 40
    stop: Optional[list[str]] = None
    presence_penalty: float = 0.0
    frequency_penalty: float = 0.0
    files: Optional[list[FileAttachment]] = None


class ChatChoice(BaseModel):
    index: int = 0
    message: Optional[dict] = None
    delta: Optional[dict] = None
    finish_reason: Optional[str] = None


class ChatUsage(BaseModel):
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0


class ChatResponse(BaseModel):
    id: str
    object: str = "chat.completion"
    created: int
    model: str
    choices: list[ChatChoice]
    usage: ChatUsage


@router.post("/chat/completions")
@router.post("/v1/chat/completions")
async def chat_completions(request: ChatRequest):
    engine = get_engine()
    messages = [m.model_dump(exclude_none=True) for m in request.messages]
    if request.files and any(f for f in request.files):
        attach = [f.model_dump() for f in request.files]
        if messages:
            msg = messages[-1]
            msg["files"] = attach
    infer_request = InferenceRequest(
        model=request.model,
        messages=messages,
        stream=request.stream,
        temperature=request.temperature,
        max_tokens=request.max_tokens,
        top_p=request.top_p,
        top_k=request.top_k,
        stop=request.stop,
        presence_penalty=request.presence_penalty,
        frequency_penalty=request.frequency_penalty,
    )

    if request.stream:
        return EventSourceResponse(
            _stream_chat(engine, infer_request, request.model)
        )

    try:
        response = await engine.chat(infer_request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return ChatResponse(
        id=f"chatcmpl-{int(time.time())}",
        created=int(time.time()),
        model=request.model,
        choices=[
            ChatChoice(
                index=0,
                message={"role": "assistant", "content": response.content},
                finish_reason=response.finish_reason,
            )
        ],
        usage=ChatUsage(
            prompt_tokens=response.tokens_in,
            completion_tokens=response.tokens_out,
            total_tokens=response.tokens_in + response.tokens_out,
        ),
    )


async def _stream_chat(
    engine: InferenceRouter,
    request: InferenceRequest,
    model: str,
) -> AsyncGenerator[dict, None]:
    yield {
        "event": "message",
        "data": json.dumps(
            {
                "id": f"chatcmpl-{int(time.time())}",
                "object": "chat.completion.chunk",
                "created": int(time.time()),
                "model": model,
                "choices": [
                    {
                        "index": 0,
                        "delta": {"role": "assistant"},
                        "finish_reason": None,
                    }
                ],
            }
        ),
    }

    try:
        async for content in engine.chat_stream(request):
            yield {
                "event": "message",
                "data": json.dumps(
                    {
                        "id": f"chatcmpl-{int(time.time())}",
                        "object": "chat.completion.chunk",
                        "created": int(time.time()),
                        "model": model,
                        "choices": [
                            {
                                "index": 0,
                                "delta": {"content": content},
                                "finish_reason": None,
                            }
                        ],
                    }
                ),
            }
    except Exception as e:
        yield {
            "event": "error",
            "data": json.dumps({"error": str(e)}),
        }
        return

    yield {
        "event": "message",
        "data": json.dumps(
            {
                "id": f"chatcmpl-{int(time.time())}",
                "object": "chat.completion.chunk",
                "created": int(time.time()),
                "model": model,
                "choices": [
                    {
                        "index": 0,
                        "delta": {},
                        "finish_reason": "stop",
                    }
                ],
            }
        ),
    }

    yield {"event": "done", "data": "[DONE]"}


@router.post("/completions")
@router.post("/v1/completions")
async def completions(request: ChatRequest):
    return await chat_completions(request)
