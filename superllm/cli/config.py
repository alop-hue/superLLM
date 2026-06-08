from __future__ import annotations

import typer
from rich.console import Console
from rich.table import Table

from superllm.config.settings import settings

console = Console()


def config_cmd(
    key: str | None = typer.Argument(None, help="Config key to get or set"),
    value: str | None = typer.Argument(None, help="Config value to set"),
    list_all: bool = typer.Option(False, "--list", "-l", help="List all config values"),
):
    """Get or set configuration values."""
    if list_all or (key is None and value is None):
        table = Table(title="superLLM Configuration")
        table.add_column("Key", style="cyan")
        table.add_column("Value", style="white")

        config_map = {
            "mode": settings.mode.value,
            "debug": str(settings.debug),
            "host": settings.host,
            "port": str(settings.port),
            "data_dir": str(settings.data_dir),
            "models_dir": str(settings.models_dir),
            "local_inference": str(settings.local_inference),
            "cloud_routing": str(settings.cloud_routing),
            "cloud_fallback": str(settings.cloud_fallback),
            "auth_enabled": str(settings.auth_enabled),
            "ui_enabled": str(settings.ui_enabled),
            "default_model": settings.default_model,
            "local_n_ctx": str(settings.local_n_ctx),
            "local_n_gpu_layers": str(settings.local_n_gpu_layers),
            "log_level": settings.log_level.value,
        }

        for k, v in sorted(config_map.items()):
            table.add_row(k, str(v))
        console.print(table)
        return

    if key and value:
        setattr(settings, key, value)
        console.print(f"[green]Set {key} = {value}[/green]")
        return

    if key:
        val = getattr(settings, key, None)
        if val is None:
            console.print(f"[red]Unknown config key: {key}[/red]")
            raise typer.Exit(1)
        console.print(f"{key} = {val}")
        return
