from __future__ import annotations

from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

from superllm.providers.registry import registry
from superllm.providers.base import Provider

console = Console()


def providers_cmd(
    action: Optional[str] = typer.Argument(None, help="Action: list, add, remove"),
    name: Optional[str] = typer.Option(None, "--name", "-n", help="Provider name"),
    type: Optional[str] = typer.Option(None, "--type", "-t", help="Provider type"),
    url: Optional[str] = typer.Option(None, "--url", "-u", help="Base URL"),
    model: Optional[str] = typer.Option(None, "--model", "-m", help="Default model"),
    enabled: bool = typer.Option(True, "--enabled/--disabled", help="Enable/disable"),
):
    """Manage inference providers."""
    import asyncio

    async def do_list():
        providers = await registry.get_providers()
        if not providers:
            console.print("No providers configured.")
            console.print("Add one with: [bold]superllm providers add --name openai --type openai[/bold]")
            return

        table = Table(title="Configured Providers")
        table.add_column("Name", style="cyan")
        table.add_column("Type", style="yellow")
        table.add_column("Enabled", style="green")
        table.add_column("Priority", style="white")
        table.add_column("Default Model", style="blue")
        table.add_column("Base URL", style="dim")

        for p in sorted(providers, key=lambda x: x.priority):
            table.add_row(
                p.name,
                p.provider_type,
                "✓" if p.is_enabled else "✗",
                str(p.priority),
                p.default_model or "-",
                p.base_url or "-",
            )
        console.print(table)

    async def do_add():
        if not name:
            console.print("[red]Error: --name is required[/red]")
            raise typer.Exit(1)
        if not type:
            console.print("[red]Error: --type is required[/red]")
            raise typer.Exit(1)

        from superllm.config.settings import ProviderType
        if type not in [t.value for t in ProviderType]:
            valid = ", ".join([t.value for t in ProviderType])
            console.print(f"[red]Invalid type. Valid types: {valid}[/red]")
            raise typer.Exit(1)

        provider = Provider(
            name=name,
            provider_type=type,
            base_url=url,
            default_model=model,
            is_enabled=enabled,
        )
        await registry.add_provider(provider)
        console.print(f"[green]Provider '{name}' added.[/green]")

    async def do_remove():
        if not name:
            console.print("[red]Error: --name is required[/red]")
            raise typer.Exit(1)
        success = await registry.remove_provider(name)
        if not success:
            console.print(f"[red]Provider '{name}' not found.[/red]")
            raise typer.Exit(1)
        console.print(f"[green]Provider '{name}' removed.[/green]")

    if action == "list" or action is None:
        asyncio.run(do_list())
    elif action == "add":
        asyncio.run(do_add())
    elif action == "remove":
        asyncio.run(do_remove())
    else:
        console.print(f"[red]Unknown action: {action}. Use: list, add, remove[/red]")
