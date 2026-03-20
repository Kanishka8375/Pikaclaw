"""Glob file matching tool."""
from __future__ import annotations

from pathlib import Path


class GlobTool:
    """Find files matching a glob pattern."""

    name = "Glob"
    description = "Find files matching a glob pattern."
    parameters = {
        "type": "object",
        "properties": {
            "pattern": {"type": "string", "description": "Glob pattern (e.g. '**/*.py')."},
            "path": {"type": "string", "description": "Directory to search in (default: current dir).", "default": "."},
        },
        "required": ["pattern"],
    }

    async def execute(self, params: dict) -> str:
        try:
            pattern = params["pattern"]
            path = params.get("path", ".")
            p = Path(path)

            if not p.exists():
                return f"Error: Path not found: {path}"

            matches = sorted(str(m) for m in p.glob(pattern) if m.is_file())

            if not matches:
                return "No matching files found."
            return "\n".join(matches)
        except Exception as e:
            return f"Error running glob: {e}"
