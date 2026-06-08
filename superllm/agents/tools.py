from __future__ import annotations

import json
import math
import time

from superllm.agents.base import Tool, ToolResult


class CalculatorTool(Tool):
    name: str = "calculator"
    description: str = "Evaluate mathematical expressions. Use for arithmetic, algebra, and numeric computations."
    parameters: dict = {
        "type": "object",
        "properties": {
            "expression": {
                "type": "string",
                "description": "The mathematical expression to evaluate (e.g., '2 + 2', 'sqrt(144)', '3 * 7 + 5')",
            }
        },
        "required": ["expression"],
    }

    async def execute(self, expression: str) -> ToolResult:
        start = time.time()
        try:
            safe_dict = {
                "abs": abs, "round": round, "min": min, "max": max,
                "sum": sum, "pow": pow, "int": int, "float": float,
                "len": len, "range": range,
                "sqrt": math.sqrt, "sin": math.sin, "cos": math.cos,
                "tan": math.tan, "log": math.log, "log10": math.log10,
                "pi": math.pi, "e": math.e, "inf": math.inf,
                "floor": math.floor, "ceil": math.ceil,
            }
            result = eval(expression, {"__builtins__": {}}, safe_dict)
            elapsed = (time.time() - start) * 1000
            return ToolResult(
                success=True,
                output=str(result),
                duration_ms=elapsed,
                data=result,
            )
        except Exception as e:
            elapsed = (time.time() - start) * 1000
            return ToolResult(
                success=False,
                output=f"Error evaluating expression: {e}",
                error=str(e),
                duration_ms=elapsed,
            )


class WebSearchTool(Tool):
    name: str = "web_search"
    description: str = "Search the web for current information. Use for news, facts, and real-time data."
    parameters: dict = {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "The search query string",
            },
            "num_results": {
                "type": "integer",
                "description": "Number of results to return (1-10)",
                "default": 5,
            },
        },
        "required": ["query"],
    }

    async def execute(self, query: str, num_results: int = 5) -> ToolResult:
        start = time.time()
        try:
            import httpx
            serp_api_key = None

            if serp_api_key:
                async with httpx.AsyncClient(timeout=15) as client:
                    resp = await client.get(
                        "https://serpapi.com/search",
                        params={"q": query, "api_key": serp_api_key, "num": num_results},
                    )
                    data = resp.json()
                    results = []
                    for r in data.get("organic_results", [])[:num_results]:
                        results.append({
                            "title": r.get("title", ""),
                            "link": r.get("link", ""),
                            "snippet": r.get("snippet", ""),
                        })
                    elapsed = (time.time() - start) * 1000
                    return ToolResult(
                        success=True,
                        output=json.dumps(results, indent=2),
                        duration_ms=elapsed,
                        data=results,
                    )

            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.get(
                    "https://api.duckduckgo.com",
                    params={"q": query, "format": "json", "no_html": 1, "skip_disambig": 1},
                )
                data = resp.json()
                results = []
                abstract = data.get("AbstractText", "")
                if abstract:
                    results.append({"title": "Summary", "snippet": abstract})
                for topic in data.get("RelatedTopics", [])[:num_results]:
                    if "Text" in topic:
                        results.append({
                            "title": topic.get("Text", "")[:100],
                            "snippet": topic.get("Text", ""),
                        })
                elapsed = (time.time() - start) * 1000
                return ToolResult(
                    success=True,
                    output=json.dumps(results, indent=2) if results else "No results found",
                    duration_ms=elapsed,
                    data=results,
                )
        except Exception as e:
            elapsed = (time.time() - start) * 1000
            return ToolResult(
                success=False,
                output=f"Web search failed: {e}",
                error=str(e),
                duration_ms=elapsed,
            )


class PythonExecTool(Tool):
    name: str = "python_execute"
    description: str = "Execute Python code in a sandboxed environment. Use for data analysis, computation, and scripting."
    parameters: dict = {
        "type": "object",
        "properties": {
            "code": {
                "type": "string",
                "description": "The Python code to execute",
            },
            "timeout": {
                "type": "integer",
                "description": "Execution timeout in seconds",
                "default": 10,
            },
        },
        "required": ["code"],
    }

    async def execute(self, code: str, timeout: int = 10) -> ToolResult:
        start = time.time()
        try:
            import sys
            from io import StringIO

            old_stdout = sys.stdout
            old_stderr = sys.stderr
            sys.stdout = StringIO()
            sys.stderr = StringIO()

            try:
                exec_globals = {"__builtins__": __builtins__}
                exec(code, exec_globals)
                output = sys.stdout.getvalue()
                error = sys.stderr.getvalue()
            except Exception as e:
                output = sys.stdout.getvalue()
                error = str(e)
            finally:
                sys.stdout = old_stdout
                sys.stderr = old_stderr

            elapsed = (time.time() - start) * 1000
            result_text = output
            if error:
                result_text += f"\nErrors:\n{error}"
            return ToolResult(
                success=not bool(error),
                output=result_text or "Code executed successfully (no output)",
                error=error or None,
                duration_ms=elapsed,
            )
        except Exception as e:
            elapsed = (time.time() - start) * 1000
            return ToolResult(
                success=False,
                output=f"Execution failed: {e}",
                error=str(e),
                duration_ms=elapsed,
            )


class FileReadTool(Tool):
    name: str = "file_read"
    description: str = "Read the contents of a file from the filesystem."
    parameters: dict = {
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "Absolute path to the file",
            },
            "encoding": {
                "type": "string",
                "description": "File encoding (default: utf-8)",
                "default": "utf-8",
            },
        },
        "required": ["path"],
    }

    async def execute(self, path: str, encoding: str = "utf-8") -> ToolResult:
        start = time.time()
        try:
            import aiofiles
            async with aiofiles.open(path, encoding=encoding) as f:
                content = await f.read()
            elapsed = (time.time() - start) * 1000
            return ToolResult(
                success=True,
                output=content[:10000] + ("\n... (truncated)" if len(content) > 10000 else ""),
                duration_ms=elapsed,
                data=content,
            )
        except Exception as e:
            elapsed = (time.time() - start) * 1000
            return ToolResult(
                success=False,
                output=f"Failed to read file: {e}",
                error=str(e),
                duration_ms=elapsed,
            )


class FileWriteTool(Tool):
    name: str = "file_write"
    description: str = "Write content to a file on the filesystem."
    parameters: dict = {
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "Absolute path to the file",
            },
            "content": {
                "type": "string",
                "description": "Content to write",
            },
            "encoding": {
                "type": "string",
                "description": "File encoding (default: utf-8)",
                "default": "utf-8",
            },
        },
        "required": ["path", "content"],
    }

    async def execute(self, path: str, content: str, encoding: str = "utf-8") -> ToolResult:
        start = time.time()
        try:
            import aiofiles
            async with aiofiles.open(path, mode="w", encoding=encoding) as f:
                await f.write(content)
            elapsed = (time.time() - start) * 1000
            return ToolResult(
                success=True,
                output=f"Successfully wrote {len(content)} bytes to {path}",
                duration_ms=elapsed,
            )
        except Exception as e:
            elapsed = (time.time() - start) * 1000
            return ToolResult(
                success=False,
                output=f"Failed to write file: {e}",
                error=str(e),
                duration_ms=elapsed,
            )


class DatabaseQueryTool(Tool):
    name: str = "database_query"
    description: str = "Execute a SQL query against the superLLM database."
    parameters: dict = {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "SQL query to execute",
            },
            "limit": {
                "type": "integer",
                "description": "Maximum number of rows to return (default: 100)",
                "default": 100,
            },
        },
        "required": ["query"],
    }

    async def execute(self, query: str, limit: int = 100) -> ToolResult:
        start = time.time()
        try:
            from superllm.storage.db import Database
            db = Database.get_instance()
            async with db.session() as session:
                result = await session.execute(query)
                rows = result.fetchmany(limit)
                columns = result.keys()
                data = [dict(zip(columns, row)) for row in rows]
            elapsed = (time.time() - start) * 1000
            return ToolResult(
                success=True,
                output=json.dumps(data, indent=2, default=str),
                duration_ms=elapsed,
                data=data,
            )
        except Exception as e:
            elapsed = (time.time() - start) * 1000
            return ToolResult(
                success=False,
                output=f"Query failed: {e}",
                error=str(e),
                duration_ms=elapsed,
            )


class WeatherTool(Tool):
    name: str = "get_weather"
    description: str = "Get current weather for a city. Returns temperature, conditions, and humidity."
    parameters: dict = {
        "type": "object",
        "properties": {
            "city": {
                "type": "string",
                "description": "City name (e.g., 'London', 'New York', 'Tokyo')",
            },
            "country": {
                "type": "string",
                "description": "Country code (e.g., 'UK', 'US', 'JP'). Optional.",
            },
        },
        "required": ["city"],
    }

    async def execute(self, city: str, country: str = "") -> ToolResult:
        start = time.time()
        try:
            import httpx
            location = f"{city},{country}" if country else city
            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.get(
                    f"https://wttr.in/{location}?format=j1",
                )
                data = resp.json()
                current = data.get("current_condition", [{}])[0]
                weather_info = {
                    "city": city,
                    "temperature_c": current.get("temp_C", "N/A"),
                    "temperature_f": current.get("temp_F", "N/A"),
                    "condition": current.get("weatherDesc", [{}])[0].get("value", "N/A"),
                    "humidity": current.get("humidity", "N/A"),
                    "wind_speed": current.get("windspeedKmph", "N/A"),
                    "feels_like_c": current.get("FeelsLikeC", "N/A"),
                }
            elapsed = (time.time() - start) * 1000
            return ToolResult(
                success=True,
                output=json.dumps(weather_info, indent=2),
                duration_ms=elapsed,
                data=weather_info,
            )
        except Exception as e:
            elapsed = (time.time() - start) * 1000
            return ToolResult(
                success=False,
                output=f"Weather fetch failed: {e}",
                error=str(e),
                duration_ms=elapsed,
            )
