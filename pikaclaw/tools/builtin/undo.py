"""Undo tool."""
from __future__ import annotations


class UndoTool:
    """Undo the last file change."""

    name = "Undo"
    description = "Undo the last file write or edit operation."
    parameters = {
        "type": "object",
        "properties": {},
        "required": [],
    }

    def __init__(self, checkpoint_manager):
        self._checkpoint = checkpoint_manager

    async def execute(self, params: dict) -> str:
        try:
            result = self._checkpoint.undo()
            if result is None:
                return "Nothing to undo."
            return f"Undone change to {result}"
        except Exception as e:
            return f"Error in undo: {e}"
