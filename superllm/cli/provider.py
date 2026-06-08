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
    api_key: Optional[str] = typer.Option(None, "--api-key", help="Provider API key"),
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
            api_key=api_key,
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

    async def do_discover():
        import httpx

        # common local ports for adapters
        candidates = {
            "ollama": "http://localhost:11434",
            "openclaw": "http://localhost:11435",
            "opencode": "http://localhost:11436",
            "openai": "http://localhost:8080",
            "deepseek": "https://api.deepseek.com",
            "openrouter": "https://openrouter.ai/api",
            "mistral": "https://api.mistral.ai",
        }

        found = []
        for ptype, base in candidates.items():
            try:
                async with httpx.AsyncClient(timeout=2) as client:
                    r = await client.get(f"{base}/models")
                    if r.status_code == 200:
                        data = r.json() or []
                        default_model = None
                        if isinstance(data, list) and len(data) > 0:
                            default_model = data[0].get("name") or data[0].get("id")
                        provider = Provider(
                            name=f"{ptype}-local",
                            provider_type=ptype,
                            base_url=base,
                            default_model=default_model,
                            is_enabled=True,
                        )
                        await registry.add_provider(provider)
                        found.append((ptype, base, default_model))
            except Exception:
                continue

        if not found:
            console.print("[yellow]No local providers discovered.[/yellow]")
            return

        for ptype, base, model in found:
            console.print(f"[green]Discovered {ptype} at {base} (default_model={model})[/green]")

    async def do_test():
        import httpx

        if not name:
            console.print("[red]Error: --name is required for test[/red]")
            raise typer.Exit(1)
        p = await registry.get_provider(name)
        if not p or not p.base_url:
            console.print(f"[red]Provider '{name}' not found or has no base_url[/red]")
            raise typer.Exit(1)
        headers = {"Authorization": f"Bearer {p.api_key}"} if getattr(p, "api_key", None) else {}
        try:
            async with httpx.AsyncClient(timeout=5, headers=headers) as client:
                r = await client.get(f"{p.base_url}/models")
                if r.status_code == 200:
                    console.print(f"[green]Provider '{name}' reachable.[/green]")
                    return
        except Exception as e:
            console.print(f"[red]Test failed: {e}[/red]")
            raise typer.Exit(1)

    async def do_types():
        from superllm.config.settings import ProviderType
        table = Table(title="Available Provider Types")
        table.add_column("Type", style="cyan")
        table.add_column("Description")
        descriptions = {
            "local": "Local models via llama.cpp",
            "openai": "OpenAI API compatible providers",
            "anthropic": "Anthropic Claude API",
            "google": "Google Gemini API",
            "deepseek": "DeepSeek API",
            "openrouter": "OpenRouter multi-model API",
            "mistral": "Mistral AI API",
            "cohere": "Cohere API",
            "xai": "xAI (Grok) API",
            "fireworks": "Fireworks AI API",
            "aws_bedrock": "AWS Bedrock",
            "azure": "Azure OpenAI",
            "together": "Together AI",
            "groq": "Groq LPU inference",
            "ollama": "Local Ollama server",
            "openclaw": "OpenClaw AI agent",
            "opencode": "Opencode AI assistant",
            "custom": "Custom OpenAI-compatible endpoint",
        }
        for t in sorted(ProviderType, key=lambda x: x.value):
            table.add_row(t.value, descriptions.get(t.value, ""))
        console.print(table)
        console.print()
        console.print("[dim]Add: [bold]superllm providers add --name my-provider --type <type> --url <url> --api-key <key>[/bold][/dim]")

    if action == "list" or action is None:
        asyncio.run(do_list())
    elif action == "add":
        asyncio.run(do_add())
    elif action == "remove":
        asyncio.run(do_remove())
    elif action == "discover":
        asyncio.run(do_discover())
    elif action == "test":
        asyncio.run(do_test())
    elif action == "types":
        asyncio.run(do_types())
    else:
        console.print(f"[red]Unknown action: {action}. Use: list, add, remove, discover, test, types[/red]")
