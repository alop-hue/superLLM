from __future__ import annotations

import typer
from rich.console import Console

from superllm.config.settings import settings

console = Console()


def serve_cmd(
    host: str = typer.Option(None, help="Host to bind to"),
    port: int = typer.Option(None, help="Port to listen on"),
    mode: str = typer.Option(None, help="Mode: local, cloud, or hybrid"),
    debug: bool = typer.Option(False, "--debug", help="Enable debug mode"),
    no_ui: bool = typer.Option(False, "--no-ui", help="Disable the web UI"),
):
    """Start the superLLM API server."""
    if host:
        settings.host = host
    if port:
        settings.port = port
    if mode:
        from superllm.config.settings import Mode
        settings.mode = Mode(mode)
    if debug:
        settings.debug = True
    if no_ui:
        settings.ui_enabled = False

    settings.ensure_dirs()

    console.print("[bold green]superLLM[/bold green] server starting...")
    console.print(f"  Mode: [bold]{settings.mode.value}[/bold]")
    console.print(f"  Host: {settings.host}")
    console.print(f"  Port: {settings.port}")
    console.print(f"  Data: {settings.data_dir}")
    console.print(f"  UI: {'enabled' if settings.ui_enabled else 'disabled'}")
    console.print()

    from superllm.server.app import run
    run()
