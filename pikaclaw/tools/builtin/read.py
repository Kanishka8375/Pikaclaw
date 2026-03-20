"""Read file tool."""
from __future__ import annotations

from pathlib import Path


class ReadTool:
    """Read file contents with line numbers."""

    name = "Read"
    description = "Read a file and return its contents with line numbers."
    parameters = {
        "type": "object",
        "properties": {
            "file_path": {"type": "string", "description": "Absolute path to the file to read."},
            "start_line": {"type": "integer", "description": "Line number to start reading from (1-indexed)."},
            "end_line": {"type": "integer", "description": "Line number to stop reading at (inclusive)."},
        },
        "required": ["file_path"],
    }

    async def execute(self, params: dict) -> str:
        try:
            file_path = params["file_path"]
            p = Path(file_path)
            if not p.exists():
                return f"Error: File not found: {file_path}"
            if p.is_dir():
                return f"Error: Path is a directory, not a file: {file_path}"

            text = p.read_text(errors="replace")
            lines = text.splitlines(keepends=True)

            start = params.get("start_line")
            end = params.get("end_line")

            if start is not None:
                start = max(1, start)
            else:
                start = 1

            if end is not None:
                end = min(len(lines), end)
            else:
                end = len(lines)

            numbered = []
            for i in range(start - 1, end):
                numbered.append(f"{i + 1:>6}\t{lines[i].rstrip()}")

            return "\n".join(numbered)
        except Exception as e:
            return f"Error reading file: {e}"
