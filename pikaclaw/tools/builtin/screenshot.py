"""Screenshot tool (placeholder)."""
from __future__ import annotations


class ScreenshotTool:
    """Take a screenshot (not available in CLI mode)."""

    name = "Screenshot"
    description = "Take a screenshot. Not available in CLI mode."
    parameters = {
        "type": "object",
        "properties": {
            "url": {"type": "string", "description": "Optional URL to screenshot."},
        },
        "required": [],
    }

    async def execute(self, params: dict) -> str:
        return "Screenshot not available in CLI mode"
