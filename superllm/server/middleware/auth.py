from __future__ import annotations

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from superllm.config.settings import settings


class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if not settings.auth_enabled:
            return await call_next(request)

        api_key = request.headers.get("Authorization", "").replace("Bearer ", "")
        if not api_key:
            api_key = request.headers.get("X-API-Key", "")

        if not api_key:
            return JSONResponse(
                status_code=401,
                content={"error": "Missing API key"},
            )

        if settings.api_key and api_key != settings.api_key:
            return JSONResponse(
                status_code=403,
                content={"error": "Invalid API key"},
            )

        return await call_next(request)
