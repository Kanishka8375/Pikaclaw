"""Sandbox executor for safe command execution."""
from __future__ import annotations
import asyncio
import os


class SandboxExecutor:
    """Wraps subprocess execution with safety constraints."""

    def __init__(self, timeout: int = 120, max_output: int = 1_000_000):
        self.timeout = timeout
        self.max_output = max_output

    async def execute(self, command: str, timeout: int | None = None, cwd: str | None = None) -> dict:
        """Execute a command with timeout and output limits."""
        t = timeout or self.timeout
        try:
            proc = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=cwd or os.getcwd(),
            )
            stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=t)
            stdout_str = stdout.decode("utf-8", errors="replace")[:self.max_output]
            stderr_str = stderr.decode("utf-8", errors="replace")[:self.max_output]
            return {
                "stdout": stdout_str,
                "stderr": stderr_str,
                "exit_code": proc.returncode,
            }
        except asyncio.TimeoutError:
            try:
                proc.kill()
            except Exception:
                pass
            return {"stdout": "", "stderr": f"Command timed out after {t}s", "exit_code": -1}
        except Exception as e:
            return {"stdout": "", "stderr": str(e), "exit_code": -1}
