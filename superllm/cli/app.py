from __future__ import annotations

import typer
from rich.console import Console

from superllm.cli.serve import serve_cmd
from superllm.cli.model import (
    pull_cmd,
    remove_cmd,
    list_cmd,
    show_cmd,
    library_cmd,
)
from superllm.cli.provider import providers_cmd
from superllm.cli.config import config_cmd
from superllm.cli.system import (
    install_cmd,
    init_cmd,
    start_cmd,
    stop_cmd,
    status_cmd,
    logs_cmd,
    doctor_cmd,
)
from superllm.cli.auth import login_cmd, logout_cmd

console = Console()

app = typer.Typer(
    name="superllm",
    help="superLLM - Local-first and cloud-capable AI platform",
    no_args_is_help=True,
    rich_markup_mode="rich",
)

# System commands
app.command("install", help="Install superLLM and its dependencies")(install_cmd)
app.command("init", help="Initialize superLLM configuration")(init_cmd)
app.command("start", help="Start the superLLM server")(start_cmd)
app.command("serve", help="Start the superLLM server (alias for start)")(serve_cmd)
app.command("stop", help="Stop the superLLM server")(stop_cmd)
app.command("status", help="Show superLLM status and health")(status_cmd)
app.command("logs", help="Show superLLM logs")(logs_cmd)
app.command("doctor", help="Run system diagnostics")(doctor_cmd)

# Auth commands
app.command("login", help="Login to superLLM cloud")(login_cmd)
app.command("logout", help="Logout from superLLM cloud")(logout_cmd)

# Model commands
app.command("pull")(pull_cmd)
app.command("remove")(remove_cmd)
app.command("list", help="List installed models")(list_cmd)
app.command("show", help="Show model details")(show_cmd)
app.command("library", help="Browse the model library")(library_cmd)

# Provider commands
app.command("providers", help="Manage providers")(providers_cmd)

# Config commands
app.command("config", help="Get or set configuration")(config_cmd)


def main():
    app()


if __name__ == "__main__":
    main()
