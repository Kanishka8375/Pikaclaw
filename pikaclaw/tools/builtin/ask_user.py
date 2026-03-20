"""Ask user tool."""
from __future__ import annotations


class AskUserTool:
    """Ask the user a question and wait for a response."""

    name = "AskUser"
    description = "Ask the user a question. Returns a special marker for the agent loop to handle."
    parameters = {
        "type": "object",
        "properties": {
            "question": {"type": "string", "description": "The question to ask the user."},
            "options": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Optional list of choices to present to the user.",
            },
        },
        "required": ["question"],
    }

    async def execute(self, params: dict) -> str:
        try:
            question = params["question"]
            options = params.get("options")

            result = f"__ASK_USER__:{question}"
            if options:
                result += f"\nOptions: {', '.join(options)}"
            return result
        except Exception as e:
            return f"Error in ask_user: {e}"
