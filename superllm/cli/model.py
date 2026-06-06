from __future__ import annotations

from typing import Optional

import typer
from rich.console import Console
from rich.table import Table
from rich.markdown import Markdown

from superllm.config.settings import settings
from superllm.models.registry import ModelRegistry
from superllm.models.library import ModelLibrary

console = Console()
registry = ModelRegistry.get_instance()


def pull_cmd(
    name: str = typer.Argument(..., help="Model name to download"),
    quantization: str = typer.Option("Q4_K_M", "--quant", "-q", help="Quantization type"),
):
    """Download a model from the library."""
    from superllm.models.library import ModelLibrary
    card = ModelLibrary.get_model(name)
    if not card:
        console.print(f"[red]Model '{name}' not found in library.[/red]")
        console.print("Run [bold]superllm library[/bold] to see available models.")
        raise typer.Exit(1)

    console.print(f"Pulling [bold]{name}[/bold] ({quantization})...")
    console.print(f"  Size estimate: {card.size_estimates.get(quantization, 'unknown')} bytes")
    console.print(f"  Recommended RAM: {card.recommended_ram}")
    console.print()

    import httpx
    import asyncio

    async def do_pull():
        models_dir = settings.models_dir
        models_dir.mkdir(parents=True, exist_ok=True)
        filename = f"{name.replace('.', '-')}-{quantization}.gguf"
        dest_path = models_dir / filename

        if dest_path.exists():
            console.print(f"[yellow]Model already exists at {dest_path}[/yellow]")
            return

        download_url = card.url
        if not download_url:
            console.print("[red]No download URL available for this model.[/red]")
            raise typer.Exit(1)

        try:
            async with httpx.AsyncClient(timeout=settings.model_pull_timeout, follow_redirects=True) as client:
                async with client.stream("GET", download_url) as response:
                    response.raise_for_status()
                    total = int(response.headers.get("content-length", 0))
                    downloaded = 0
                    with open(dest_path, "wb") as f:
                        async for chunk in response.aiter_bytes(chunk_size=8192):
                            f.write(chunk)
                            downloaded += len(chunk)
                            if total:
                                pct = (downloaded / total) * 100
                                console.print(f"\r  Downloading: {pct:.1f}% ({downloaded / 1024 / 1024:.1f} MB / {total / 1024 / 1024:.1f} MB)", end="")
                            else:
                                console.print(f"\r  Downloaded: {downloaded / 1024 / 1024:.1f} MB", end="")
                    console.print()
        except Exception as e:
            if dest_path.exists():
                dest_path.unlink()
            console.print(f"[red]Download failed: {e}[/red]")
            raise typer.Exit(1)

        await registry.register_model(
            name=name,
            path=dest_path,
            architecture=card.architecture,
            parameter_count=card.parameter_count,
            context_length=card.context_length,
            quant=quantization,
            tags=card.tags,
            capabilities=card.capabilities,
        )
        console.print(f"[green]Successfully downloaded {name} ({quantization})[/green]")
        console.print(f"  Path: {dest_path}")
        console.print(f"  Size: {registry._format_size(dest_path.stat().st_size)}")

    asyncio.run(do_pull())


def remove_cmd(
    name: str = typer.Argument(..., help="Model name to remove"),
    force: bool = typer.Option(False, "--force", "-f", help="Force remove without confirmation"),
):
    """Remove a downloaded model."""
    import asyncio

    if not force:
        confirm = typer.confirm(f"Remove model '{name}'?")
        if not confirm:
            console.print("Cancelled.")
            raise typer.Exit(0)

    async def do_remove():
        success = await registry.remove_model(name)
        if not success:
            console.print(f"[red]Model '{name}' not found.[/red]")
            raise typer.Exit(1)
        console.print(f"[green]Model '{name}' removed.[/green]")

    asyncio.run(do_remove())


def list_cmd():
    """List installed models."""
    import asyncio

    async def do_list():
        models = await registry.list_installed()
        if not models:
            console.print("No models installed.")
            console.print("Run [bold]superllm pull <model>[/bold] to download one.")
            return

        table = Table(title="Installed Models")
        table.add_column("Name", style="cyan")
        table.add_column("Architecture", style="yellow")
        table.add_column("Parameters", style="green")
        table.add_column("Size", style="magenta")
        table.add_column("Quant", style="blue")
        table.add_column("Context", style="white")
        table.add_column("Used", style="white")

        for m in sorted(models, key=lambda x: x.name):
            table.add_row(
                m.name,
                m.architecture or "-",
                m.parameter_count or "-",
                m._format_size(m.size_bytes),
                m.quant or "-",
                str(m.context_length),
                str(m.use_count or 0),
            )
        console.print(table)

        stats = await registry.get_stats()
        console.print(f"\n[dim]Total: {stats['total_models']} models ({stats['total_size_display']})[/dim]")

    asyncio.run(do_list())


def show_cmd(
    name: str = typer.Argument(..., help="Model name"),
):
    """Show detailed model information."""
    import asyncio

    async def do_show():
        model = await registry.get_model(name)
        if not model:
            console.print(f"[red]Model '{name}' not found locally.[/red]")
            card = ModelLibrary.get_model(name)
            if card:
                console.print(f"\n[yellow]'{name}' is available in the library.[/yellow]")
                console.print(f"  Run [bold]superllm pull {name}[/bold] to download it.")
            raise typer.Exit(1)

        d = model.to_dict()
        card = ModelLibrary.get_model(name)

        console.print(f"\n[bold cyan]{d['name']}[/bold cyan]")
        console.print(f"  Display: {d['display_name']}")
        console.print(f"  Path: {d['path']}")
        console.print(f"  Size: {d['size_display']}")
        console.print(f"  Architecture: {d['architecture'] or '-'}")
        console.print(f"  Parameters: {d['parameter_count'] or '-'}")
        console.print(f"  Context Length: {d['context_length']}")
        console.print(f"  Quantization: {d['quant'] or '-'}")
        console.print(f"  Type: {d['model_type']}")
        console.print(f"  Downloaded: {d['download_date']}")
        console.print(f"  Last Used: {d['last_used'] or 'Never'}")
        console.print(f"  Use Count: {d['use_count']}")

        if d["tags"]:
            console.print(f"  Tags: {', '.join(d['tags'])}")

        caps = d.get("capabilities", {})
        if caps:
            cap_list = [k for k, v in caps.items() if v]
            console.print(f"  Capabilities: {', '.join(cap_list)}")

        if card:
            console.print(f"\n  [bold]Library Info:[/bold]")
            console.print(f"  Description: {card.description}")
            console.print(f"  Category: {card.category}")
            console.print(f"  Recommended RAM: {card.recommended_ram}")
            console.print(f"  URL: {card.url}")

    asyncio.run(do_show())


def library_cmd(
    query: str = typer.Argument("", help="Search query"),
    category: Optional[str] = typer.Option(None, "--category", "-c", help="Filter by category"),
    tag: Optional[str] = typer.Option(None, "--tag", "-t", help="Filter by tag"),
):
    """Browse the model library."""
    if category or tag:
        tags = [tag] if tag else None
        results = ModelLibrary.filter(category=category, tags=tags)
    else:
        results = ModelLibrary.search(query)

    if not results:
        console.print(f"No models found matching '{query}'")
        return

    table = Table(title=f"Model Library ({len(results)} models)")
    table.add_column("Name", style="cyan")
    table.add_column("Parameters", style="green")
    table.add_column("Context", style="white")
    table.add_column("Category", style="yellow")
    table.add_column("Tags", style="blue")
    table.add_column("RAM", style="magenta")

    for m in sorted(results, key=lambda x: x.parameter_count):
        table.add_row(
            m.name,
            m.parameter_count,
            str(m.context_length),
            m.category,
            ", ".join(m.tags[:3]) + ("..." if len(m.tags) > 3 else ""),
            m.recommended_ram or "-",
        )
    console.print(table)
    console.print(f"\n[dim]Tip: Run [bold]superllm pull <model>[/bold] to download[/dim]")
