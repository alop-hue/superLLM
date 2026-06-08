from __future__ import annotations

import asyncio
import os
import platform
import sys

import typer
from rich.console import Console
from rich.table import Table

from superllm.config.settings import Mode, settings

console = Console()


def install_cmd(
    with_local: bool = typer.Option(False, "--local", help="Install local inference dependencies"),
    with_cloud: bool = typer.Option(False, "--cloud", help="Install cloud inference dependencies"),
    dev: bool = typer.Option(False, "--dev", help="Install development dependencies"),
):
    """Install superLLM and its optional dependencies."""
    console.print("[bold green]superLLM Installer[/bold green]")
    console.print()

    deps = []
    if with_local:
        deps.append("local")
    if with_cloud:
        deps.append("cloud")
    if dev:
        deps.append("dev")

    if not deps:
        console.print("[yellow]No optional dependencies selected.[/yellow]")
        console.print("  Use --local for local inference (llama-cpp-python)")
        console.print("  Use --cloud for cloud inference (litellm)")
        console.print("  Use --dev for development tools")
        console.print()
        console.print("[green]Core dependencies are already installed with the package.[/green]")
        return

    extra = ",".join(deps)
    cmd = f"pip install 'superllm[{extra}]'"

    console.print(f"Run: [bold]{cmd}[/bold]")
    confirm = typer.confirm("Proceed with installation?", default=True)
    if not confirm:
        console.print("Cancelled.")
        return

    os.system(cmd)
    console.print("[green]Installation complete![/green]")


def init_cmd(
    force: bool = typer.Option(False, "--force", "-f", help="Force re-initialization"),
):
    """Initialize superLLM configuration and directories."""
    settings.ensure_dirs()
    config_path = settings.data_dir / "config.yaml"

    if config_path.exists() and not force:
        console.print(f"[yellow]Configuration already exists at {config_path}[/yellow]")
        console.print("Use --force to reinitialize.")
        return

    os.makedirs(settings.models_dir, exist_ok=True)
    os.makedirs(settings.data_dir, exist_ok=True)

    console.print("[bold green]superLLM initialized![/bold green]")
    console.print(f"  Data directory: {settings.data_dir}")
    console.print(f"  Models directory: {settings.models_dir}")
    console.print(f"  Default mode: {settings.mode.value}")
    console.print()
    console.print("Run [bold]superllm start[/bold] to start the server.")
    console.print("Run [bold]superllm pull <model>[/bold] to download a model.")


def start_cmd(
    host: str = typer.Option(None, help="Host to bind to"),
    port: int = typer.Option(None, help="Port to listen on"),
    mode: str = typer.Option(None, help="Mode: local, cloud, or hybrid"),
    debug: bool = typer.Option(False, "--debug", help="Enable debug mode"),
    no_ui: bool = typer.Option(False, "--no-ui", help="Disable the web UI"),
):
    """Start the superLLM server."""
    settings.ensure_dirs()

    if host:
        settings.host = host
    if port:
        settings.port = port
    if mode:
        settings.mode = Mode(mode)
    if debug:
        settings.debug = True
    if no_ui:
        settings.ui_enabled = False

    console.print("[bold green]superLLM[/bold green] v0.1.0")
    console.print(f"  Mode: [bold]{settings.mode.value}[/bold]")
    console.print(f"  Server: http://{settings.host}:{settings.port}")
    console.print(f"  Docs: http://{settings.host}:{settings.port}/docs")
    console.print(f"  Data: {settings.data_dir}")
    console.print(f"  Models: {settings.models_dir}")
    console.print(f"  UI: {'enabled' if settings.ui_enabled else 'disabled'}")

    from superllm.server.app import run

    run()


def stop_cmd():
    """Stop the superLLM server."""
    import httpx

    try:
        httpx.get(f"http://{settings.host}:{settings.port}/api/shutdown", timeout=5)
        console.print("[green]Server stopped.[/green]")
    except Exception:
        console.print("[yellow]Could not connect to server. It may not be running.[/yellow]")


def status_cmd():
    """Show superLLM system status."""
    import httpx

    async def check():
        console.print("[bold]superLLM Status[/bold]")
        console.print("  Version: 0.1.0")
        console.print(f"  Platform: {platform.system()} ({platform.machine()})")
        console.print(f"  Python: {sys.version.split()[0]}")
        console.print(f"  Data Dir: {settings.data_dir}")
        console.print(f"  Models Dir: {settings.models_dir}")
        console.print(f"  Mode: {settings.mode.value}")

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"http://{settings.host}:{settings.port}/api/status",
                    timeout=5,
                )
                if response.status_code == 200:
                    data = response.json()
                    console.print(
                        f"  Server: [green]Running[/green] on http://{settings.host}:{settings.port}"
                    )
                    console.print(f"  Provider: {data.get('provider', '?')}")
                    console.print(
                        f"  Provider Healthy: [{'green' if data.get('provider_healthy') else 'red'}]{data.get('provider_healthy', '?')}[/]"  # noqa: E501
                    )
                    models = data.get("models", {})
                    console.print(
                        f"  Installed Models: {models.get('total_models', 0)} ({models.get('total_size_display', '0')})"  # noqa: E501
                    )
                else:
                    console.print(
                        f"  Server: [yellow]Responding with {response.status_code}[/yellow]"
                    )
        except Exception:
            console.print("  Server: [red]Not running[/red]")
            console.print("  Start with: [bold]superllm start[/bold]")

        # Hardware detection
        console.print("\n[bold]Hardware:[/bold]")
        import psutil

        console.print(f"  CPU: {psutil.cpu_count()} cores")
        mem = psutil.virtual_memory()
        console.print(
            f"  RAM: {mem.total / (1024**3):.1f} GB total ({mem.available / (1024**3):.1f} GB free)"
        )
        try:
            import GPUtil

            gpus = GPUtil.getGPUs()
            for gpu in gpus:
                console.print(f"  GPU: {gpu.name} ({gpu.memoryFree}MB free)")
        except ImportError:
            console.print("  GPU: [yellow]GPUtil not installed[/yellow]")

        # Installed models
        from superllm.models.registry import ModelRegistry

        registry = ModelRegistry.get_instance()
        models = await registry.list_installed()
        if models:
            console.print("\n[bold]Installed Models:[/bold]")
            for m in models:
                console.print(f"  • {m.name} ({m._format_size(m.size_bytes)})")

    asyncio.run(check())


def logs_cmd(
    lines: int = typer.Option(50, "--lines", "-n", help="Number of lines to show"),
    follow: bool = typer.Option(False, "--follow", "-f", help="Follow log output"),
):
    """Show superLLM logs."""
    log_file = settings.data_dir / "superllm.log"
    if not log_file.exists():
        console.print("[yellow]No log file found.[/yellow]")
        console.print(f"  Expected at: {log_file}")
        return

    if follow:
        os.system(f"tail -f {log_file}")
    else:
        os.system(f"tail -n {lines} {log_file}")


def doctor_cmd():
    """Run system diagnostics to check superLLM health."""
    import importlib

    console.print("[bold]superLLM Diagnostics[/bold]")
    console.print()

    checks = []

    # Python version
    py_version = sys.version_info
    checks.append(
        (
            "Python >= 3.10",
            py_version.major >= 3 and py_version.minor >= 10,
            f"{py_version.major}.{py_version.minor}.{py_version.micro}",
        )
    )

    # Core dependencies
    for dep in ["typer", "fastapi", "uvicorn", "pydantic", "sqlalchemy", "httpx", "rich", "yaml"]:
        try:
            importlib.import_module(dep.replace("-", "_"))
            checks.append((f"Core: {dep}", True, "installed"))
        except ImportError:
            checks.append((f"Core: {dep}", False, "missing"))

    # Optional dependencies
    _llama_available = importlib.util.find_spec("llama_cpp") is not None
    if _llama_available:
        checks.append(("Local: llama-cpp-python", True, "installed"))
    else:
        checks.append(
            ("Local: llama-cpp-python", False, "not installed (run superllm install --local)")
        )

    _litellm_available = importlib.util.find_spec("litellm") is not None
    if _litellm_available:
        checks.append(("Cloud: litellm", True, "installed"))
    else:
        checks.append(("Cloud: litellm", False, "not installed (run superllm install --cloud)"))

    # Directories
    for d in [settings.data_dir, settings.models_dir]:
        exists = d.exists()
        checks.append((f"Dir: {d}", exists, "exists" if exists else "missing"))

    # Config
    checks.append(("Mode", True, settings.mode.value))
    checks.append(("Auth", True, "enabled" if settings.auth_enabled else "disabled"))
    checks.append(("UI", True, "enabled" if settings.ui_enabled else "disabled"))

    table = Table(title="Diagnostic Results")
    table.add_column("Check", style="cyan")
    table.add_column("Status", style="white")
    table.add_column("Detail", style="dim")

    all_pass = True
    for name, passed, detail in checks:
        status = "[green]✓[/green]" if passed else "[red]✗[/red]"
        if not passed:
            all_pass = False
        table.add_row(name, status, detail)

    console.print(table)

    if all_pass:
        console.print("\n[bold green]All checks passed![/bold green]")
    else:
        console.print("\n[yellow]Some checks failed. See above for details.[/yellow]")
