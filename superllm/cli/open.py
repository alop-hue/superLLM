from __future__ import annotations

import asyncio
import os
import shutil
import subprocess
import sys
import webbrowser
from typing import Optional

import httpx
import typer
from rich.console import Console
from rich.table import Table

from superllm.config.settings import settings

console = Console()


APP_DEFINITIONS: dict[str, dict] = {
    "opencode": {
        "binary": "opencode",
        "description": "AI coding assistant (terminal-based)",
        "env_prefix": "OPENAI",
        "needs_server": True,
    },
    "openclaw": {
        "binary": "openclaw",
        "description": "AI coding agent (terminal-based)",
        "env_prefix": "OPENAI",
        "needs_server": True,
    },
    "claude-code": {
        "binary": "claude",
        "description": "Anthropic's Claude Code CLI",
        "env_prefix": "ANTHROPIC",
        "needs_server": False,
    },
    "aider": {
        "binary": "aider",
        "description": "AI pair programming in terminal",
        "env_prefix": "OPENAI",
        "needs_server": True,
    },
}


def _load_app_definitions() -> dict[str, dict]:
    import json
    from pathlib import Path
    definitions = dict(APP_DEFINITIONS)
    custom_path = settings.data_dir / "apps.json"
    if custom_path.exists():
        try:
            custom = json.loads(custom_path.read_text())
            if isinstance(custom, dict):
                definitions.update(custom)
        except Exception:
            pass
    return definitions


def _find_app(app_name: str) -> str | None:
    return shutil.which(app_name)


async def _is_server_running() -> bool:
    try:
        async with httpx.AsyncClient(timeout=3) as c:
            r = await c.get(f"http://{settings.host}:{settings.port}/api/health")
            return r.status_code < 500
    except Exception:
        return False


def _start_server() -> subprocess.Popen | None:
    console.print("[yellow]Starting superLLM server...[/yellow]")
    try:
        proc = subprocess.Popen(
            [sys.executable, "-m", "superllm", "start"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        return proc
    except Exception as e:
        console.print(f"[red]Failed to start server: {e}[/red]")
        return None


async def _wait_for_server(timeout: int = 30) -> bool:
    import time
    start = time.time()
    with console.status("[yellow]Waiting for server to start...[/yellow]") as status:
        while time.time() - start < timeout:
            if await _is_server_running():
                return True
            await asyncio.sleep(0.5)
    return False


def _ensure_server():
    already_running = asyncio.run(_is_server_running())
    if not already_running:
        proc = _start_server()
        if not proc:
            console.print("[red]Could not start server.[/red]")
            raise typer.Exit(1)
        if not asyncio.run(_wait_for_server()):
            console.print("[red]Server failed to start in time. Check logs with 'superllm logs'[/red]")
            raise typer.Exit(1)
        console.print("[green]Server is running.[/green]")
    return True


def _launch_app(app_name: str, model: str | None, extra_args: list[str] | None = None):
    app_def = _load_app_definitions().get(app_name)
    if not app_def:
        console.print(f"[red]Unknown app: {app_name}. Use 'superllm open list' to see available apps.[/red]")
        raise typer.Exit(1)

    binary = _find_app(app_def["binary"])
    if not binary:
        console.print(f"[red]'{app_def['binary']}' not found in PATH.[/red]")
        console.print(f"  {app_def['description']}")
        console.print(f"  Install it first, then try again.")
        raise typer.Exit(1)

    if app_def.get("needs_server") and model:
        _ensure_server()

    base_url = f"http://{settings.host}:{settings.port}"
    env = os.environ.copy()

    if app_def["env_prefix"] == "OPENAI":
        env["OPENAI_BASE_URL"] = f"{base_url}/v1"
        env["OPENAI_API_KEY"] = "superllm-local"
        if model:
            env["OPENAI_MODEL"] = model
    elif app_def["env_prefix"] == "ANTHROPIC":
        env["ANTHROPIC_BASE_URL"] = base_url
        if model:
            env["ANTHROPIC_MODEL"] = model

    cmd = [binary]
    if model:
        if app_name == "opencode":
            cmd.extend(["--model", model])
        elif app_name == "aider":
            cmd.extend(["--model", f"openai/{model}"])
        elif app_name == "openclaw":
            cmd.extend(["--model", model])
    if extra_args:
        cmd.extend(extra_args)

    console.print(f"[green]Launching {app_name}...[/green]")
    console.print(f"  Command: {' '.join(cmd)}")
    try:
        subprocess.run(cmd, env=env)
    except KeyboardInterrupt:
        console.print(f"\n[yellow]{app_name} closed.[/yellow]")


# ============================================================
# Typer app (sub-group)
# ============================================================
open_app = typer.Typer(
    help="Open superLLM or launch external AI tools with its models",
    no_args_is_help=False,
)


@open_app.callback(invoke_without_command=True)
def open_default(
    ctx: typer.Context,
    model: Optional[str] = typer.Option(None, "--model", "-m", help="Model to pre-select in the UI"),
    host: Optional[str] = typer.Option(None, "--host", help="Server host"),
    port: Optional[int] = typer.Option(None, "--port", "-p", help="Server port"),
):
    """Open the superLLM web UI in your browser."""
    if ctx.invoked_subcommand is not None:
        return

    if host:
        settings.host = host
    if port:
        settings.port = port

    _ensure_server()

    base_url = f"http://{settings.host}:{settings.port}"
    url = f"{base_url}/?model={model}" if model else base_url

    console.print(f"[green]Opening {url}[/green]")
    webbrowser.open(url)


@open_app.command("list")
def open_list():
    """List available apps that can be launched with superLLM models."""
    table = Table(title="Available superLLM Launcher Apps")
    table.add_column("App", style="cyan")
    table.add_column("Binary", style="yellow")
    table.add_column("Description")
    table.add_column("Installed", style="green")

    for name, info in _load_app_definitions().items():
        installed = _find_app(info["binary"]) is not None
        table.add_row(
            name,
            info["binary"],
            info["description"],
            "✓" if installed else "✗",
        )
    console.print(table)
    console.print()
    console.print("[dim]Usage: [bold]superllm open <app> --model <model>[/bold][/dim]")
    console.print("[dim]       [bold]superllm open[/bold]  → open web UI in browser[/dim]")


@open_app.command("opencode")
def open_opencode(
    model: Optional[str] = typer.Option(None, "--model", "-m", help="Model to use"),
):
    """Launch opencode with a superLLM model."""
    _launch_app("opencode", model)


@open_app.command("openclaw")
def open_openclaw(
    model: Optional[str] = typer.Option(None, "--model", "-m", help="Model to use"),
):
    """Launch openclaw with a superLLM model."""
    _launch_app("openclaw", model)


@open_app.command("claude-code")
def open_claude_code(
    model: Optional[str] = typer.Option(None, "--model", "-m", help="Model to use"),
):
    """Launch claude-code with a superLLM model."""
    _launch_app("claude-code", model)


@open_app.command("aider")
def open_aider(
    model: Optional[str] = typer.Option(None, "--model", "-m", help="Model to use"),
):
    """Launch aider with a superLLM model."""
    _launch_app("aider", model)


def open_cmd(
    ctx: typer.Context,
    model: Optional[str] = typer.Option(None, "--model", "-m", help="Model to pre-select in the UI"),
    host: Optional[str] = typer.Option(None, "--host", help="Server host"),
    port: Optional[int] = typer.Option(None, "--port", "-p", help="Server port"),
):
    """Legacy callback - delegates to new group-based open."""
    open_default(ctx, model=model, host=host, port=port)
