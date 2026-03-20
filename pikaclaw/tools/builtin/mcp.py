"""MCP tool (placeholder)."""
from __future__ import annotations


class MCPTool:
    """Interface with Model Context Protocol servers."""

    name = "MCP"
    description = "Call a tool on an MCP server. Requires MCP configuration."
    parameters = {
        "type": "object",
        "properties": {
            "server": {"type": "string", "description": "MCP server name."},
            "tool": {"type": "string", "description": "Tool name on the MCP server."},
        },
        "required": [],
    }

    async def execute(self, params: dict) -> str:
        return "MCP not configured"
