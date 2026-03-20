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
                console.print("[cyan]/feedback[/cyan] — Rate the last response")
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
            elif cmd == "/feedback" or cmd.startswith("/feedback "):
                _handle_feedback(cmd, state, console)
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


def _handle_feedback(cmd: str, state, console):
    """Interactive feedback collection from the user."""
    import asyncio
    from pikaclaw.feedback.collector import FeedbackCollector, CATEGORIES

    console.print("\n[bold yellow]📝 Feedback[/bold yellow]")
    console.print("[dim]Help PikaClaw improve by rating the last response.[/dim]\n")

    # Rating
    console.print("  [cyan]Rate (1-5):[/cyan] 1=terrible 2=bad 3=ok 4=good 5=great")
    try:
        rating_str = console.input("  Rating: ").strip()
        rating = int(rating_str) if rating_str.isdigit() else 0
        rating = max(0, min(5, rating))
    except (KeyboardInterrupt, EOFError):
        console.print("[dim]Feedback cancelled.[/dim]")
        return

    # Category
    cat_list = sorted(CATEGORIES - {"other"})
    console.print(f"\n  [cyan]Category:[/cyan] {', '.join(cat_list)}")
    try:
        category = console.input("  Category (or Enter to skip): ").strip().lower()
        if category not in CATEGORIES:
            category = "other"
    except (KeyboardInterrupt, EOFError):
        category = "other"

    # Comment
    try:
        comment = console.input("  Comment (optional): ").strip()
    except (KeyboardInterrupt, EOFError):
        comment = ""

    # Build conversation snippet
    snippet = "\n".join(
        f"{m.get('role', '?')}: {str(m.get('content', ''))[:100]}"
        for m in state.messages[-6:]
    )

    # Submit
    async def _submit():
        collector = FeedbackCollector()
        entry_id = await collector.submit(
            rating=rating,
            category=category,
            comment=comment,
            session_id=state.session_id,
            agent=state.active_agent,
            model=state.current_model or "",
            turn_count=state.turn_count,
            conversation_snippet=snippet,
            source="explicit",
        )
        return entry_id

    try:
        entry_id = asyncio.run(_submit())
        console.print(f"\n  [green]✓ Feedback recorded ({entry_id})[/green]")
        if rating <= 2:
            console.print("  [dim]Darwin will analyze this and work on improvements.[/dim]")
    except Exception as e:
        console.print(f"  [red]Failed to save feedback: {e}[/red]")


@cli.command()
def feedback():
    """View feedback summary and satisfaction metrics."""
    import asyncio
    from pikaclaw.feedback.collector import FeedbackCollector
    from pikaclaw.feedback.analyzer import FeedbackAnalyzer
    from rich.table import Table

    async def _show():
        collector = FeedbackCollector()
        analyzer = FeedbackAnalyzer(collector)

        score = await collector.get_satisfaction_score(days=7)
        patterns = await analyzer.analyze(days=7, min_count=1)
        trend = await analyzer.get_trend(days=7)

        # Summary
        console.print(Panel.fit(
            f"[bold]Last 7 days[/bold]\n"
            f"Total feedback: {score['total_feedback']}\n"
            f"Avg rating: {score['avg_rating']}/5\n"
            f"Resolution rate: {score['resolution_rate']:.0%}\n"
            f"Top complaint: {score['top_complaint'] or 'none'}",
            title="📊 Feedback Summary",
            border_style="yellow",
        ))

        # Patterns
        if patterns:
            table = Table(title="Feedback Patterns (Darwin targets)")
            table.add_column("Category", style="cyan")
            table.add_column("Severity", style="red")
            table.add_column("Count")
            table.add_column("Description")
            for p in patterns[:10]:
                table.add_row(
                    p.weakness_category,
                    f"{p.severity:.0%}",
                    str(p.count),
                    p.description[:80],
                )
            console.print(table)

        # Trend
        if trend:
            console.print("\n[bold]Daily trend:[/bold]")
            for day in trend[:7]:
                bar = "█" * day["count"]
                console.print(f"  {day['date']}  {bar} {day['count']} ({day['avg_rating']}/5)")

    asyncio.run(_show())


def main():
    """Main entry point."""
    cli()
