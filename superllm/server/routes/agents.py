from __future__ import annotations

import json
import time
from collections.abc import AsyncGenerator

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from sse_starlette.sse import EventSourceResponse

from superllm.agents import (
    AgentExecutor,
    CalculatorTool,
    DatabaseQueryTool,
    FileReadTool,
    FileWriteTool,
    PythonExecTool,
    WeatherTool,
    WebSearchTool,
)

router = APIRouter()


class AgentRequest(BaseModel):
    prompt: str
    model: str = "auto"
    stream: bool = False
    max_iterations: int = 10
    tools: list[str] = None
    temperature: float = 0.3


class AgentResponse(BaseModel):
    response: str
    iterations: int = 0
    total_time_ms: float = 0.0


AVAILABLE_TOOLS = {
    "calculator": CalculatorTool,
    "web_search": WebSearchTool,
    "python_execute": PythonExecTool,
    "file_read": FileReadTool,
    "file_write": FileWriteTool,
    "database_query": DatabaseQueryTool,
    "get_weather": WeatherTool,
}

DEFAULT_TOOLS = ["calculator", "web_search", "python_execute"]


def _build_agent(request: AgentRequest) -> AgentExecutor:
    tool_names = request.tools or DEFAULT_TOOLS
    tools = []
    for name in tool_names:
        if name in AVAILABLE_TOOLS:
            tools.append(AVAILABLE_TOOLS[name]())
    return AgentExecutor(
        tools=tools,
        model=request.model,
        max_iterations=request.max_iterations,
    )


@router.post("/agent/run")
async def agent_run(request: AgentRequest):
    agent = _build_agent(request)
    start = time.time()

    if request.stream:
        return EventSourceResponse(_stream_agent(agent, request))

    try:
        result = await agent.run(request.prompt, stream=False)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent execution failed: {e}")

    elapsed = (time.time() - start) * 1000
    return AgentResponse(
        response=result,
        iterations=agent.max_iterations,
        total_time_ms=elapsed,
    )


async def _stream_agent(agent: AgentExecutor, request: AgentRequest) -> AsyncGenerator[dict, None]:
    yield {
        "event": "message",
        "data": json.dumps({"type": "start", "message": "Agent starting..."}),
    }

    try:
        async for chunk in agent.run(request.prompt, stream=True):
            if isinstance(chunk, str):
                yield {
                    "event": "message",
                    "data": json.dumps({"type": "chunk", "content": chunk}),
                }
    except Exception as e:
        yield {
            "event": "error",
            "data": json.dumps({"type": "error", "error": str(e)}),
        }
        return

    yield {
        "event": "message",
        "data": json.dumps({"type": "done", "message": "[DONE]"}),
    }


@router.get("/agent/tools")
async def list_tools():
    return {
        "tools": [
            {
                "name": name,
                "description": tool_cls.description,
                "parameters": tool_cls.parameters,
            }
            for name, tool_cls in AVAILABLE_TOOLS.items()
        ],
        "total": len(AVAILABLE_TOOLS),
    }
