"""PikaClaw CLI entry point."""
from __future__ import annotations
import asyncio
import click
from rich.console import Console
from rich.panel import Panel

console = Console()


@click.group(invoke_without_command=True)
@click.option("--no-gui", is_flag=True, help="Run in terminal mode")
@click.pass_context
def cli(ctx, no_gui):
    """PikaClaw — AI coding agent."""
    if ctx.invoked_subcommand is None:
        if no_gui:
            _run_interactive()
        else:
            # Try desktop, fall back to terminal
            try:
                from pikaclaw.desktop.app import launch
                launch()
            except Exception:
                _run_interactive()


@cli.command()
def version():
    """Show PikaClaw version."""
    from pikaclaw import __version__
    console.print(f"PikaClaw v{__version__}")


@cli.command()
def doctor():
    """Run system health check."""
    from pikaclaw.setup.doctor import run_doctor
    run_doctor()


@cli.command()
def setup():
    """Run first-time setup."""
    from pikaclaw.setup.installer import run_first_time_setup
    run_first_time_setup()


@cli.command()
@click.option("--host", default="0.0.0.0", help="Server host")
@click.option("--port", default=8420, help="Server port")
def serve(host, port):
    """Start HTTP API server."""
    import uvicorn
    uvicorn.run("pikaclaw.server.main:app", host=host, port=port, reload=False)


@cli.command()
def chat():
    """Interactive terminal chat."""
    _run_interactive()


@cli.command()
def init():
    """Create PIKACLAW.md in current directory."""
    from pathlib import Path
    p = Path("PIKACLAW.md")
    if p.exists():
        console.print("[yellow]PIKACLAW.md already exists[/yellow]")
        return
    p.write_text("# Project Instructions\n\nDescribe your project here. PikaClaw reads this file for context.\n")
    console.print("[green]Created PIKACLAW.md[/green]")


def _run_interactive():
    """Run interactive terminal chat loop."""
    from pikaclaw.config.loader import load_config
    from pikaclaw.core.agent_loop import AgentLoop, LoopState
    from pikaclaw.models.router import ModelRouter
    from pikaclaw.tools.registry import ToolRegistry
    from pikaclaw.agents.registry import AGENTS
    from pikaclaw.security.permissions import PermissionEvaluator

    config = load_config()
    loop = AgentLoop(
        model_router=ModelRouter(config),
        tool_registry=ToolRegistry(),
        permission_system=PermissionEvaluator(config),
        context_manager=None,
        memory=None,
        agent_registry=AGENTS,
        config=config,
    )
    state = LoopState()

    console.print(Panel.fit(
        "[bold cyan]PikaClaw[/bold cyan] v0.1.0\n"
        f"Model: {config.default_model}\n"
        "Type /help for commands, Ctrl+C to exit",
        title="⚡ PikaClaw",
        border_style="cyan",
    ))

    while True:
        try:
            user_input = console.input("[bold green]> [/bold green]")
        except (KeyboardInterrupt, EOFError):
            console.print("\n[dim]Goodbye![/dim]")
            break

        if not user_input.strip():
            continue

        # Handle slash commands
        if user_input.strip().startswith("/"):
            cmd = user_input.strip().lower()
            if cmd == "/help":
                console.print("[cyan]/agent <name>[/cyan] — Switch agent (build, plan, review, debug)")
                console.print("[cyan]/model <name>[/cyan] — Switch model")
                console.print("[cyan]/status[/cyan] — Show status")
                console.print("[cyan]/clear[/cyan] — Clear conversation")
                console.print("[cyan]/cost[/cyan] — Show token usage")
                console.print("[cyan]/quit[/cyan] — Exit")
                continue
            elif cmd == "/status":
                console.print(f"Agent: {state.active_agent} | Model: {state.current_model} | Turns: {state.turn_count}")
                continue
            elif cmd == "/clear":
                state = LoopState()
                console.print("[dim]Conversation cleared.[/dim]")
                continue
            elif cmd == "/cost":
                console.print(f"Tokens: {state.total_input_tokens + state.total_output_tokens} | Cost: ${state.total_cost:.4f}")
                continue
            elif cmd.startswith("/agent "):
                name = cmd.split(" ", 1)[1].strip()
                if name in AGENTS:
                    state.active_agent = name
                    console.print(f"[cyan]Switched to {AGENTS[name].display_name} {AGENTS[name].icon}[/cyan]")
                else:
                    console.print(f"[red]Unknown agent: {name}[/red]")
                continue
            elif cmd in ("/quit", "/exit"):
                break

        # Run agent loop
        try:
            async def _run():
                async for msg in loop.run(user_input, state):
                    if msg.type == "text":
                        console.print(msg.text)
                    elif msg.type == "tool_call":
                        console.print(f"[dim]→ {msg.tool}({', '.join(f'{k}={repr(v)[:50]}' for k, v in msg.input.items())})[/dim]")
                    elif msg.type == "tool_result":
                        if msg.is_error:
                            console.print(f"[red]Error: {msg.result[:200]}[/red]")
                    elif msg.type == "error":
                        console.print(f"[red]{msg.error}[/red]")
                    elif msg.type == "done":
                        console.print(f"[dim]({msg.turns} turns, {msg.tokens} tokens)[/dim]")

            asyncio.run(_run())
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")


def main():
    """Main entry point."""
    cli()
