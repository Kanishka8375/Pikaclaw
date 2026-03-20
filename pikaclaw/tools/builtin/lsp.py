"""LSP tool (placeholder)."""
from __future__ import annotations


class LSPTool:
    """Interface with Language Server Protocol."""

    name = "LSP"
    description = "Query a Language Server for code intelligence. Requires LSP configuration."
    parameters = {
        "type": "object",
        "properties": {
            "action": {"type": "string", "description": "LSP action (e.g. 'definition', 'references', 'hover')."},
            "file_path": {"type": "string", "description": "File path for the LSP query."},
        },
        "required": [],
    }

    async def execute(self, params: dict) -> str:
        return "LSP not configured"
