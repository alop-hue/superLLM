from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

router = APIRouter()

UI_DIST = Path(__file__).parent.parent.parent / "ui" / "dist"


def mount_ui(app):
    if not UI_DIST.exists():
        return

    ui_router = APIRouter()

    if (UI_DIST / "index.html").exists():
        ui_router.mount("/static", StaticFiles(directory=str(UI_DIST / "assets")), name="ui_static")

        @ui_router.get("/{full_path:path}")
        async def serve_ui(full_path: str):
            file_path = UI_DIST / full_path
            if file_path.exists() and not file_path.is_dir():
                return FileResponse(str(file_path))
            return FileResponse(str(UI_DIST / "index.html"))

        app.mount("/", ui_router, name="ui")
