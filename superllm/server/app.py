from __future__ import annotations

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from superllm.config.settings import settings
from superllm.server.routes.chat import router as chat_router
from superllm.server.routes.models import router as models_router
from superllm.server.routes.health import router as health_router
from superllm.server.routes.config import router as config_router
from superllm.server.routes.providers import router as providers_router
from superllm.server.routes.conversations import router as conversations_router
from superllm.server.middleware.auth import AuthMiddleware
from superllm.storage.db import Database
from superllm.storage.models import Base


def create_app() -> FastAPI:
    app = FastAPI(
        title="superLLM API",
        description="Local-first and cloud-capable AI platform API",
        version="0.1.0",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.add_middleware(AuthMiddleware)

    # API routes under /api
    app.include_router(health_router, prefix="/api", tags=["Health"])
    app.include_router(models_router, prefix="/api", tags=["Models"])
    app.include_router(chat_router, prefix="/api", tags=["Chat"])
    app.include_router(config_router, prefix="/api", tags=["Config"])
    app.include_router(providers_router, prefix="/api", tags=["Providers"])
    app.include_router(conversations_router, prefix="/api", tags=["Conversations"])

    # OpenAI-compatible routes at root level (for SDK compatibility)
    app.include_router(chat_router, prefix="", tags=["OpenAI"])
    app.include_router(models_router, prefix="", tags=["OpenAI"])

    @app.on_event("startup")
    async def startup():
        db = Database.get_instance()
        await db.connect()
        async with db.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    @app.on_event("shutdown")
    async def shutdown():
        db = Database.get_instance()
        await db.disconnect()

    return app


def run():
    app = create_app()
    uvicorn.run(
        app,
        host=settings.host,
        port=settings.port,
        log_level=settings.log_level.value,
        reload=settings.debug,
        reload_dirs=[str(settings.data_dir.parent)] if settings.debug else None,
    )


def run_dev():
    import sys
    uvicorn.run(
        "superllm.server.app:create_app",
        host=settings.host,
        port=settings.port,
        log_level=settings.log_level.value,
        reload=True,
        factory=True,
    )
