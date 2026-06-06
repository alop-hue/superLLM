from __future__ import annotations

import typer
from rich.console import Console

console = Console()


def login_cmd():
    """Login to superLLM cloud."""
    console.print("[yellow]Cloud login is not yet implemented.[/yellow]")
    console.print("This will be available in a future release.")
    console.print("For now, use [bold]superllm start[/bold] in local mode.")


def logout_cmd():
    """Logout from superLLM cloud."""
    console.print("[yellow]Cloud logout is not yet implemented.[/yellow]")
