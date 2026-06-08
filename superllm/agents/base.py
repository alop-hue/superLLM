from __future__ import annotations

import json
from abc import ABC, abstractmethod
from collections.abc import AsyncGenerator
from dataclasses import dataclass, field
from typing import Any

from superllm.inference.base import InferenceRequest
from superllm.inference.smart_router import SmartRouter, TaskClassifier
from superllm.models.library import ModelLibrary


@dataclass
class ToolResult:
    success: bool
    output: str
    error: str | None = None
    duration_ms: float = 0.0
    data: Any = None


class Tool(ABC):
    name: str = ""
    description: str = ""
    parameters: dict = field(default_factory=dict)

    @abstractmethod
    async def execute(self, **kwargs) -> ToolResult:
        ...

    def to_openai_tool(self) -> dict:
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters,
            },
        }


@dataclass
class AgentMemory:
    messages: list[dict] = field(default_factory=list)
    max_messages: int = 50
    system_prompt: str = ""

    def add_message(self, role: str, content: str):
        self.messages.append({"role": role, "content": content})
        if len(self.messages) > self.max_messages:
            self.messages = [self.messages[0]] + self.messages[-(self.max_messages - 1):]

    def get_context(self) -> list[dict]:
        if self.system_prompt and (not self.messages or self.messages[0].get("role") != "system"):
            return [{"role": "system", "content": self.system_prompt}] + self.messages
        return self.messages

    def clear(self):
        self.messages = []


class AgentExecutor:
    def __init__(
        self,
        tools: list[Tool] = None,
        model: str = "auto",
        max_iterations: int = 5,
        system_prompt: str = None,
    ):
        self.tools = tools or []
        self.model = model
        self.max_iterations = max_iterations
        self.router = SmartRouter()
        self.memory = AgentMemory()
        self.classifier = TaskClassifier()

        self.memory.system_prompt = system_prompt or self._default_system_prompt()

    def _default_system_prompt(self) -> str:
        tools_desc = "\n".join(
            f"  - {t.name}: {t.description}" for t in self.tools
        )
        return f"""You are a capable AI assistant with access to the following tools:

{tools_desc}

To use a tool, respond with a JSON block in this format:
```tool
{{"name": "tool_name", "arguments": {{"arg1": "value1"}}}}
```

After receiving the tool result, continue the conversation naturally.
You can use multiple tools sequentially to solve complex problems.
When you have the final answer, respond normally without the tool block."""

    def add_tool(self, tool: Tool):
        self.tools.append(tool)

    async def _detect_tool_call(self, content: str) -> tuple[str, dict] | None:
        if "```tool" in content:
            parts = content.split("```tool")
            for part in parts[1:]:
                json_str = part.split("```")[0].strip()
                try:
                    parsed = json.loads(json_str)
                    return parsed.get("name"), parsed.get("arguments", {})
                except json.JSONDecodeError:
                    continue

        try:
            parsed = json.loads(content)
            if isinstance(parsed, dict) and "name" in parsed and "arguments" in parsed:
                return parsed["name"], parsed["arguments"]
        except (json.JSONDecodeError, ValueError):
            pass

        return None

    async def _execute_tool(self, name: str, arguments: dict) -> ToolResult:
        for tool in self.tools:
            if tool.name == name:
                return await tool.execute(**arguments)
        return ToolResult(
            success=False,
            output=f"Tool '{name}' not found",
            error=f"Unknown tool: {name}",
        )

    async def run(
        self, user_input: str, stream: bool = False
    ) -> str | AsyncGenerator[str, None]:
        self.memory.add_message("user", user_input)

        if stream:
            return self._run_stream()
        return await self._run_sync()

    async def _run_sync(self) -> str:
        for iteration in range(self.max_iterations):
            context = self.memory.get_context()

            agent_model = self.model
            if agent_model == "auto":
                candidates = ModelLibrary.recommend_for_task("agent", max_ram=32.0)
                if candidates:
                    agent_model = candidates[0].name
                else:
                    agent_model = "llama3.2-3b"

            request = InferenceRequest(
                model=agent_model,
                messages=context,
                temperature=0.3,
                max_tokens=2048,
            )

            try:
                response = await self.router.chat(request)
            except Exception:
                request.model = "llama3.2-3b"
                response = await self.router.chat(request)

            content = response.content.strip()
            self.memory.add_message("assistant", content)

            tool_call = await self._detect_tool_call(content)
            if tool_call is None:
                return content

            name, args = tool_call
            result = await self._execute_tool(name, args)
            result_str = f"Tool '{name}' result: {result.output}"
            if result.error:
                result_str += f"\nError: {result.error}"
            self.memory.add_message("user", result_str)

        return f"Maximum iterations reached. Response: {self.memory.messages[-1]['content']}"

    async def _run_stream(self) -> AsyncGenerator[str, None]:
        for iteration in range(self.max_iterations):
            context = self.memory.get_context()

            agent_model = self.model
            if agent_model == "auto":
                candidates = ModelLibrary.recommend_for_task("agent", max_ram=32.0)
                agent_model = candidates[0].name if candidates else "llama3.2-3b"

            request = InferenceRequest(
                model=agent_model,
                messages=context,
                temperature=0.3,
                max_tokens=2048,
                stream=True,
            )

            full_content = ""
            try:
                async for chunk in self.router.chat_stream(request):
                    full_content += chunk
                    yield chunk
            except Exception:
                request.model = "llama3.2-3b"
                async for chunk in self.router.chat_stream(request):
                    full_content += chunk
                    yield chunk

            self.memory.add_message("assistant", full_content)

            tool_call = await self._detect_tool_call(full_content)
            if tool_call is None:
                return

            name, args = tool_call
            yield f"\n\n[Using tool: {name}...]\n\n"
            result = await self._execute_tool(name, args)
            result_str = f"Tool result: {result.output}"
            if result.error:
                result_str += f"\nError: {result.error}"
            self.memory.add_message("user", result_str)
            yield result_str + "\n\n"

        yield "\n[Reached maximum iterations]"

    def clear_memory(self):
        self.memory.clear()
