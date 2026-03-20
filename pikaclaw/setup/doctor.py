"""System health check."""
from __future__ import annotations
import sys
import shutil
from pathlib import Path
from rich.console import Console
from rich.table import Table

console = Console()


def run_doctor():
    """Run comprehensive system health check."""
    table = Table(title="PikaClaw Doctor", show_header=True)
    table.add_column("Check", style="cyan")
    table.add_column("Status")
    table.add_column("Details", style="dim")

    # Python version
    py_ver = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    py_ok = sys.version_info >= (3, 11)
    table.add_row("Python", "[green]✓[/green]" if py_ok else "[red]✗[/red]", f"v{py_ver}")

    # Ollama
    ollama_ok = False
    ollama_detail = "Not running"
    try:
        import httpx
        resp = httpx.get("http://localhost:11434/api/tags", timeout=3)
        if resp.status_code == 200:
            models = [m["name"] for m in resp.json().get("models", [])]
            ollama_ok = True
            ollama_detail = f"{len(models)} models: {', '.join(models[:3])}"
    except Exception:
        pass
    table.add_row("Ollama", "[green]✓[/green]" if ollama_ok else "[yellow]⚠[/yellow]", ollama_detail)

    # Config
    home_cfg = Path.home() / ".pikaclaw" / "config.json"
    cwd_cfg = Path.cwd() / "pikaclaw.json"
    cfg_exists = home_cfg.exists() or cwd_cfg.exists()
    cfg_path = str(cwd_cfg) if cwd_cfg.exists() else str(home_cfg) if home_cfg.exists() else "None"
    table.add_row("Config", "[green]✓[/green]" if cfg_exists else "[yellow]⚠[/yellow]", cfg_path)

    # Disk space
    import psutil
    disk = psutil.disk_usage("/")
    free_gb = disk.free / (1024**3)
    table.add_row("Disk Space", "[green]✓[/green]" if free_gb > 5 else "[yellow]⚠[/yellow]", f"{free_gb:.1f} GB free")

    # Git
    git_ok = shutil.which("git") is not None
    table.add_row("Git", "[green]✓[/green]" if git_ok else "[red]✗[/red]", "Installed" if git_ok else "Not found")

    # GPU (optional)
    gpu_detail = "No nvidia-smi"
    try:
        import subprocess
        r = subprocess.run(["nvidia-smi", "--query-gpu=name,memory.total", "--format=csv,noheader"],
                          capture_output=True, text=True, timeout=5)
        if r.returncode == 0:
            gpu_detail = r.stdout.strip()
    except Exception:
        pass
    table.add_row("GPU", "[green]✓[/green]" if "nvidia" not in gpu_detail.lower() or gpu_detail != "No nvidia-smi" else "[dim]-[/dim]", gpu_detail)

    console.print(table)
