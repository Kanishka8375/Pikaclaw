"""Edit file tool."""
from __future__ import annotations

from pathlib import Path


class EditTool:
    """Find and replace text in a file."""

    name = "Edit"
    description = "Edit a file by replacing old_text with new_text. The old_text must appear exactly once in the file."
    parameters = {
        "type": "object",
        "properties": {
            "file_path": {"type": "string", "description": "Absolute path to the file to edit."},
            "old_text": {"type": "string", "description": "The exact text to find and replace (must be unique in file)."},
            "new_text": {"type": "string", "description": "The replacement text."},
        },
        "required": ["file_path", "old_text", "new_text"],
    }

    def __init__(self, checkpoint_manager):
        self._checkpoint = checkpoint_manager

    async def execute(self, params: dict) -> str:
        try:
            file_path = params["file_path"]
            old_text = params["old_text"]
            new_text = params["new_text"]

            p = Path(file_path)
            if not p.exists():
                return f"Error: File not found: {file_path}"

            content = p.read_text(errors="replace")
            count = content.count(old_text)

            if count == 0:
                return "Error: old_text not found in file."
            if count > 1:
                return f"Error: old_text found {count} times. It must be unique. Provide more surrounding context."

            new_content = content.replace(old_text, new_text, 1)
            p.write_text(new_content)

            self._checkpoint.save(file_path, content, new_content)

            return f"Successfully edited {file_path}"
        except Exception as e:
            return f"Error editing file: {e}"
