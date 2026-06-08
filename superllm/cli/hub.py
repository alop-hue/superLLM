from __future__ import annotations

import typer
from rich.console import Console
from rich.prompt import Prompt
from rich.table import Table

console = Console()


def _save_env_token(token: str):
    from pathlib import Path

    key = "SUPERLLM_HF_TOKEN"
    env_path = Path.cwd() / ".env"
    if env_path.exists():
        lines = env_path.read_text().splitlines()
        found = False
        for i, line in enumerate(lines):
            if line.strip().startswith(f"{key}="):
                lines[i] = f"{key}={token}"
                found = True
                break
        if not found:
            lines.append(f"{key}={token}")
        env_path.write_text("\n".join(lines) + "\n")
    else:
        env_path.write_text(f"{key}={token}\n")


def _show_results_table(results: list[dict], limit: int) -> list[dict]:
    sorted_results = sorted(results, key=lambda x: x["downloads"], reverse=True)[:limit]
    table = Table(title=f"HuggingFace GGUF Models ({len(sorted_results)} found)")
    table.add_column("#", style="dim", justify="right")
    table.add_column("Model ID", style="cyan")
    table.add_column("Downloads", style="green", justify="right")
    table.add_column("Likes", style="yellow", justify="right")
    table.add_column("Pipeline", style="white")
    table.add_column("Gated", style="red")

    for i, m in enumerate(sorted_results, 1):
        table.add_row(
            str(i),
            m["id"],
            f"{m['downloads']:,}",
            str(m["likes"]),
            m.get("pipeline_tag") or "-",
            "[red]Y[/red]" if m["is_gated"] else "",
        )
    console.print(table)
    return sorted_results


def _interactive_browse(client, results: list[dict]):
    while True:
        sorted_results = _show_results_table(results, 200)
        console.print()
        console.print(
            "[bold]Commands:[/bold] [cyan]#[/cyan] view details, [cyan]d #[/cyan] download, [cyan]q[/cyan] quit"  # noqa: E501
        )
        cmd = Prompt.ask("Select", default="q").strip().lower()

        if cmd == "q":
            break

        parts = cmd.split(maxsplit=1)
        if parts[0] == "d" and len(parts) > 1:
            try:
                idx = int(parts[1]) - 1
                model_id = sorted_results[idx]["id"]
                console.print(f"[green]Downloading {model_id}...[/green]")
                console.print(f"  Run: [bold]superllm pull {model_id}[/bold]")
            except (ValueError, IndexError):
                console.print("[red]Invalid selection.[/red]")
            continue

        try:
            idx = int(cmd) - 1
            model_id = sorted_results[idx]["id"]
        except (ValueError, IndexError):
            console.print("[red]Invalid selection.[/red]")
            continue

        repo_info = client.get_repo_info(model_id)
        if not repo_info:
            console.print(f"[red]Could not fetch details for {model_id}.[/red]")
            continue

        console.print(f"\n[bold cyan]{model_id}[/bold cyan]")
        console.print(f"  Downloads: {repo_info.downloads:,}")
        console.print(f"  Likes: {repo_info.likes:,}")
        console.print(f"  Pipeline: {repo_info.pipeline_tag or 'N/A'}")
        console.print(f"  Gated: {'[red]Yes[/red]' if repo_info.is_gated else '[green]No[/green]'}")
        console.print(f"  Created: {repo_info.created_at or 'N/A'}")

        if repo_info.gguf_files:
            console.print(f"\n  [bold]GGUF Files ({len(repo_info.gguf_files)}):[/bold]")
            for f in repo_info.gguf_files[:20]:
                size = ""
                for s in repo_info.siblings:
                    if s["rfilename"] == f:
                        bytes_size = s.get("size", 0)
                        if bytes_size:
                            size = f" ({bytes_size / 1024 / 1024:.0f} MB)"
                        break
                quant = f.replace(".gguf", "").split("-")[-1]
                console.print(f"    {quant:12s} {f}{size}")
        else:
            console.print("\n  [yellow]No GGUF files found in this repo.[/yellow]")

        action = Prompt.ask(
            "[bold]Actions[/bold]",
            choices=["back", "pull", "open", "quit"],
            default="back",
        )
        if action == "pull":
            console.print(f"  Run: [bold]superllm pull {model_id}[/bold]")
        elif action == "open":
            console.print(f"  Run: [bold]superllm open --model {model_id}[/bold]")
        elif action == "quit":
            break
        console.print()


def hub_cmd(
    query: str = typer.Argument("", help="Search query"),
    pipeline: str | None = typer.Option(
        None,
        "--pipeline",
        "-p",
        help="Filter by pipeline tag (text-generation, image-text-to-text, etc.)",
    ),
    limit: int = typer.Option(25, "--limit", "-l", help="Max results"),
    info: str | None = typer.Option(None, "--info", "-i", help="Show info for a specific model ID"),
    token_status: bool = typer.Option(False, "--token-status", "-t", help="Check HF token status"),
    login: bool = typer.Option(False, "--login", help="Set HuggingFace token"),
    interactive: bool = typer.Option(False, "--interactive", "-I", help="Interactive browse mode"),
):
    """Browse and search HuggingFace Hub for GGUF models."""
    from superllm.config.settings import settings
    from superllm.hub.hf_client import HFClient

    client = HFClient()

    if token_status:
        ok, msg = client.validate_token()
        if ok:
            console.print(f"[green]✓ {msg}[/green]")
        else:
            console.print(f"[yellow]✗ {msg}[/yellow]")
            console.print("  Set token: [bold]superllm hub --login[/bold]")
        return

    if login:
        token = typer.prompt("HuggingFace Access Token", hide_input=True)
        _save_env_token(token)
        settings.hf_token = token
        client = HFClient(token=token)
        ok, msg = client.validate_token()
        if ok:
            console.print(f"[green]✓ Token saved. {msg}[/green]")
        else:
            console.print("[red]Invalid token.[/red]")
        return

    if info:
        repo_info = client.get_repo_info(info)
        if not repo_info:
            console.print(f"[red]Model '{info}' not found.[/red]")
            raise typer.Exit(1)

        console.print(f"\n[bold cyan]{info}[/bold cyan]")
        console.print(f"  Downloads: {repo_info.downloads:,}")
        console.print(f"  Likes: {repo_info.likes:,}")
        console.print(f"  Pipeline: {repo_info.pipeline_tag or 'N/A'}")
        console.print(f"  Gated: {'[red]Yes[/red]' if repo_info.is_gated else '[green]No[/green]'}")
        console.print(f"  Created: {repo_info.created_at or 'N/A'}")

        if repo_info.gguf_files:
            console.print(f"\n  [bold]GGUF Files ({len(repo_info.gguf_files)}):[/bold]")
            for f in repo_info.gguf_files[:20]:
                size = ""
                for s in repo_info.siblings:
                    if s["rfilename"] == f:
                        bytes_size = s.get("size", 0)
                        if bytes_size:
                            size = f" ({bytes_size / 1024 / 1024:.0f} MB)"
                        break
                quant = f.replace(".gguf", "").split("-")[-1]
                console.print(f"    {quant:12s} {f}{size}")
        else:
            console.print("\n  [yellow]No GGUF files found in this repo.[/yellow]")
        return

    console.print(f"[dim]Searching HuggingFace Hub for '{query or 'popular GGUF models'}'...[/dim]")
    from superllm.models.library import ModelLibrary

    results = ModelLibrary.search_hub(query, pipeline_tag=pipeline, limit=limit)

    if not results:
        console.print("[yellow]No GGUF models found matching your query.[/yellow]")
        console.print("Try: [bold]superllm hub llama[/bold] or [bold]superllm hub qwen[/bold]")
        console.print("Or use: [bold]superllm hub --interactive[/bold] to browse with selections")
        return

    if interactive:
        _interactive_browse(client, results)
        return

    sorted_results = _show_results_table(results, limit)
    console.print(
        f"\n[dim]Details: [bold]superllm hub --info {sorted_results[0]['id']}[/bold][/dim]"
    )
    console.print("[dim]Browse: [bold]superllm hub --interactive[/bold] for interactive mode[/dim]")
    console.print(f"[dim]Install: [bold]superllm pull {sorted_results[0]['id']}[/bold][/dim]")
    console.print(
        f"[dim]Open UI: [bold]superllm open --model {sorted_results[0]['id']}[/bold][/dim]"
    )
