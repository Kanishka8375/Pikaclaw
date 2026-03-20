"""Bash command execution tool."""
from __future__ import annotations

import asyncio


class BashTool:
    """Execute shell commands."""

    name = "Bash"
    description = "Execute a bash command and return stdout, stderr, and exit code."
    parameters = {
        "type": "object",
        "properties": {
            "command": {"type": "string", "description": "The shell command to execute."},
            "timeout": {"type": "integer", "description": "Timeout in seconds (default 120).", "default": 120},
        },
        "required": ["command"],
    }

    async def execute(self, params: dict) -> str:
        try:
            command = params["command"]
            timeout = params.get("timeout", 120)

            proc = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            try:
                stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=timeout)
            except asyncio.TimeoutError:
                proc.kill()
                await proc.communicate()
                return f"Error: Command timed out after {timeout}s"

            result_parts = []
            if stdout:
                result_parts.append(stdout.decode(errors="replace"))
            if stderr:
                result_parts.append(stderr.decode(errors="replace"))

            output = "\n".join(result_parts).strip()
            exit_code = proc.returncode

            if output:
                return f"{output}\n\nExit code: {exit_code}"
            return f"Exit code: {exit_code}"
        except Exception as e:
            return f"Error executing command: {e}"
