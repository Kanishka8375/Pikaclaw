"""Redo tool."""
from __future__ import annotations


class RedoTool:
    """Redo the last undone file change."""

    name = "Redo"
    description = "Redo the last undone file write or edit operation."
    parameters = {
        "type": "object",
        "properties": {},
        "required": [],
    }

    def __init__(self, checkpoint_manager):
        self._checkpoint = checkpoint_manager

    async def execute(self, params: dict) -> str:
        try:
            result = self._checkpoint.redo()
            if result is None:
                return "Nothing to redo."
            return f"Redone change to {result}"
        except Exception as e:
            return f"Error in redo: {e}"
