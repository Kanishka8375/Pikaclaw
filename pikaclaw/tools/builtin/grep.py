"""Grep search tool."""
from __future__ import annotations

import asyncio


class GrepTool:
    """Search file contents using grep."""

    name = "Grep"
    description = "Search for a pattern in files using grep -rn."
    parameters = {
        "type": "object",
        "properties": {
            "pattern": {"type": "string", "description": "Regular expression pattern to search for."},
            "path": {"type": "string", "description": "Directory or file to search in (default: current dir).", "default": "."},
            "include": {"type": "string", "description": "File glob pattern to include (e.g. '*.py')."},
        },
        "required": ["pattern"],
    }

    async def execute(self, params: dict) -> str:
        try:
            pattern = params["pattern"]
            path = params.get("path", ".")
            include = params.get("include")

            cmd_parts = ["grep", "-rn"]
            if include:
                cmd_parts.extend(["--include", include])
            cmd_parts.extend(["--", pattern, path])

            # Shell-escape properly
            import shlex
            cmd = " ".join(shlex.quote(p) for p in cmd_parts)

            proc = await asyncio.create_subprocess_shell(
                cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=30)

            output = stdout.decode(errors="replace").strip()
            if not output:
                return "No matches found."
            return output
        except asyncio.TimeoutError:
            return "Error: grep timed out after 30s"
        except Exception as e:
            return f"Error running grep: {e}"
