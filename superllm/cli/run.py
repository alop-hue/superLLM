from __future__ import annotations

import asyncio
import readline
import sys
from typing import Optional

import typer
from rich.console import Console
from rich.markdown import Markdown

from superllm.inference.base import InferenceRequest
from superllm.inference.router import InferenceRouter, RoutingStrategy
from superllm.models.library import ModelLibrary
from superllm.models.registry import ModelRegistry

console = Console()


def _show_help():
    console.print("[bold]Commands:[/bold]")
    console.print("  [cyan]/exit[/cyan], [cyan]/quit[/cyan], [cyan]/q[/cyan]  Exit the chat")
    console.print("  [cyan]/clear[/cyan], [cyan]/cls[/cyan]          Clear the screen")
    console.print("  [cyan]/help[/cyan], [cyan]/h[/cyan], [cyan]/?[/cyan]       Show this help message")
    console.print("  [cyan]/info[/cyan]               Show model information")
    console.print("  [cyan]/raw[/cyan]                Toggle raw text output (default: formatted)")
    console.print()
    console.print("[bold]Tips:[/bold]")
    console.print("  Use [cyan]\"\"\"[/cyan] to start multi-line input, end with [cyan]\"\"\"[/cyan] on its own line")
    console.print("  Press [bold]Ctrl+C[/bold] or [bold]Ctrl+D[/bold] to exit")


async def _show_model_info(model_name: str):
    registry = ModelRegistry.get_instance()
    installed = await registry.get_model(model_name)
    card = ModelLibrary.get_model(model_name)

    console.print(f"[bold cyan]{model_name}[/bold cyan]")
    if card:
        console.print(f"  Display: {card.display_name}")
        console.print(f"  Description: {card.description}")
        console.print(f"  Architecture: {card.architecture}")
        console.print(f"  Parameters: {card.parameter_count}")
        console.print(f"  Context: {card.context_length} tokens")
        console.print(f"  Source: {card.source}")
    if installed:
        console.print(f"  [green]✓ Installed[/green]")
        console.print(f"  Path: {installed.path}")
    console.print()


def _read_multiline(prompt: str) -> str:
    sys.stdout.write(prompt)
    sys.stdout.flush()
    first = input()
    stripped = first.strip()
    if stripped == '"""':
        lines = []
        while True:
            try:
                line = input()
            except EOFError:
                break
            if line.strip() == '"""':
                break
            lines.append(line)
        return "\n".join(lines)
    return first


async def _do_run(
    model: str,
    local: bool = False,
    cloud: bool = False,
    system: Optional[str] = None,
    temperature: float = 0.7,
    max_tokens: Optional[int] = None,
):
    registry = ModelRegistry.get_instance()
    router = InferenceRouter()

    is_cloud_model = ":cloud" in model

    if cloud or is_cloud_model:
        router.set_strategy(RoutingStrategy.cloud_only)
    elif local:
        router.set_strategy(RoutingStrategy.local_only)

    installed = await registry.get_model(model)
    if not installed and not is_cloud_model:
        card = ModelLibrary.get_model(model)
        if not card or card.source == "cloud":
            pass
        else:
            console.print(f"[yellow]Model '{model}' is not downloaded.[/yellow]")
            console.print(f"  Run [bold]superllm pull {model}[/bold] to download it first.")
            raise typer.Exit(1)

    conversation: list[dict] = []
    if system:
        conversation.append({"role": "system", "content": system})

    console.print()
    console.print(f"[bold cyan]╭─ superLLM chat ───────────────────────────────╮")
    console.print(f"│ Model: {model}")
    if system:
        console.print(f"│ System: {system[:50]}{'...' if len(system) > 50 else ''}")
    console.print(f"│ Type [bold]/help[/bold] for commands, [bold]/exit[/bold] to quit")
    console.print(f"╰──────────────────────────────────────────────────╯")
    console.print()

    raw_mode = False

    while True:
        try:
            user_input = _read_multiline(f"[bold cyan]{model}[/bold cyan] >>> ")
        except (EOFError, KeyboardInterrupt):
            console.print()
            break

        if not user_input.strip():
            continue

        if user_input.startswith("/"):
            parts = user_input[1:].strip().split(maxsplit=1)
            cmd = parts[0].lower()
            args = parts[1] if len(parts) > 1 else ""

            if cmd in ("exit", "quit", "q"):
                break
            elif cmd in ("clear", "cls"):
                console.clear()
                continue
            elif cmd in ("help", "h", "?"):
                _show_help()
                continue
            elif cmd == "info":
                await _show_model_info(model)
                continue
            elif cmd == "raw":
                raw_mode = not raw_mode
                console.print(f"  Raw mode: {'[green]on[/green]' if raw_mode else '[yellow]off[/yellow]'}")
                continue
            else:
                console.print(f"[yellow]Unknown command: /{cmd}[/yellow]")
                console.print("  Type [bold]/help[/bold] for available commands")
                continue

        conversation.append({"role": "user", "content": user_input})

        request = InferenceRequest(
            model=model,
            messages=conversation,
            stream=True,
            temperature=temperature,
            max_tokens=max_tokens,
        )

        try:
            full_response = ""
            async for chunk in router.chat_stream(request):
                if isinstance(chunk, str):
                    full_response += chunk
                    sys.stdout.write(chunk)
                    sys.stdout.flush()

            conversation.append({"role": "assistant", "content": full_response})

            if full_response and not raw_mode:
                sys.stdout.write("\n\n")
                sys.stdout.flush()
            elif full_response:
                sys.stdout.write("\n")
                sys.stdout.flush()
        except Exception as e:
            console.print(f"\n[red]Error: {e}[/red]")
            conversation.pop()
            continue


def run_cmd(
    model: str = typer.Argument(..., help="Model name to chat with"),
    local: bool = typer.Option(False, "--local", "-l", help="Force local inference"),
    cloud: bool = typer.Option(False, "--cloud", "-c", help="Force cloud inference"),
    system: Optional[str] = typer.Option(None, "--system", "-s", help="System prompt"),
    temperature: float = typer.Option(0.7, "--temperature", "-t", help="Temperature (0.0-2.0)"),
    max_tokens: Optional[int] = typer.Option(None, "--max-tokens", "-m", help="Max tokens to generate"),
):
    """Start an interactive chat with a model (like 'ollama run')."""
    asyncio.run(
        _do_run(
            model=model,
            local=local,
            cloud=cloud,
            system=system,
            temperature=temperature,
            max_tokens=max_tokens,
        )
    )
