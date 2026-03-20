"""First-run setup and installation."""
from __future__ import annotations
import json
from pathlib import Path
from rich.console import Console
from rich.panel import Panel

console = Console()
PIKACLAW_DIR = Path.home() / ".pikaclaw"


def is_first_run() -> bool:
    """Check if PikaClaw has been set up."""
    return not (PIKACLAW_DIR / ".initialized").exists()


def run_first_time_setup():
    """Run first-time setup wizard."""
    console.print(Panel.fit(
        "[bold cyan]PikaClaw First-Time Setup[/bold cyan]",
        border_style="cyan",
    ))

    # Create directories
    for d in ["keys", "logs", "sessions", "memory", "skills", "agents", "darwin"]:
        (PIKACLAW_DIR / d).mkdir(parents=True, exist_ok=True)
    console.print("[green]✓[/green] Created ~/.pikaclaw directories")

    # Check Ollama
    try:
        import httpx
        resp = httpx.get("http://localhost:11434/api/tags", timeout=5)
        if resp.status_code == 200:
            models = [m["name"] for m in resp.json().get("models", [])]
            console.print(f"[green]✓[/green] Ollama running with {len(models)} models: {', '.join(models[:5])}")
        else:
            console.print("[yellow]⚠[/yellow] Ollama is running but returned unexpected status")
    except Exception:
        console.print("[yellow]⚠[/yellow] Ollama not running. Install from https://ollama.com")

    # Save default config
    config_path = PIKACLAW_DIR / "config.json"
    if not config_path.exists():
        default_config = {
            "default_model": "ollama/qwen2.5-coder:3b",
            "routing": "balanced",
            "default_agent": "build",
            "security": {"sandbox_enabled": True, "audit_logging": True},
        }
        config_path.write_text(json.dumps(default_config, indent=2))
        console.print("[green]✓[/green] Saved default config")

    # Mark as initialized
    (PIKACLAW_DIR / ".initialized").touch()
    console.print("\n[bold green]Setup complete![/bold green] Run [cyan]pikaclaw[/cyan] to start.")
