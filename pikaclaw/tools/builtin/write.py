"""Write file tool."""
from __future__ import annotations

from pathlib import Path


class WriteTool:
    """Write content to a file, creating parent directories as needed."""

    name = "Write"
    description = "Write content to a file. Creates parent directories if they don't exist."
    parameters = {
        "type": "object",
        "properties": {
            "file_path": {"type": "string", "description": "Absolute path to the file to write."},
            "content": {"type": "string", "description": "Content to write to the file."},
        },
        "required": ["file_path", "content"],
    }

    def __init__(self, checkpoint_manager):
        self._checkpoint = checkpoint_manager

    async def execute(self, params: dict) -> str:
        try:
            file_path = params["file_path"]
            content = params["content"]
            p = Path(file_path)

            old_content = ""
            if p.exists():
                old_content = p.read_text(errors="replace")

            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(content)

            self._checkpoint.save(file_path, old_content, content)

            return f"Successfully wrote {len(content)} bytes to {file_path}"
        except Exception as e:
            return f"Error writing file: {e}"
