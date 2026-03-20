"""Git tool."""
from __future__ import annotations

import asyncio
import shlex


class GitTool:
    """Run git commands."""

    name = "Git"
    description = "Run a git subcommand."
    parameters = {
        "type": "object",
        "properties": {
            "subcommand": {"type": "string", "description": "Git subcommand (e.g. 'status', 'log', 'diff')."},
            "args": {"type": "string", "description": "Additional arguments for the git subcommand.", "default": ""},
        },
        "required": ["subcommand"],
    }

    async def execute(self, params: dict) -> str:
        try:
            subcommand = params["subcommand"]
            args = params.get("args", "")

            cmd = f"git {shlex.quote(subcommand)}"
            if args:
                cmd += f" {args}"

            proc = await asyncio.create_subprocess_shell(
                cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=30)

            result_parts = []
            if stdout:
                result_parts.append(stdout.decode(errors="replace"))
            if stderr:
                result_parts.append(stderr.decode(errors="replace"))

            output = "\n".join(result_parts).strip()
            if output:
                return output
            return f"git {subcommand} completed (exit code {proc.returncode})"
        except asyncio.TimeoutError:
            return "Error: git command timed out after 30s"
        except Exception as e:
            return f"Error running git: {e}"
