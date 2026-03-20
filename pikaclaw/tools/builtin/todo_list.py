"""Todo list tool."""
from __future__ import annotations


class TodoListTool:
    """Manage an in-memory task list."""

    name = "TodoList"
    description = "Create and manage a task list. Supports create, check, uncheck, list, and clear actions."
    parameters = {
        "type": "object",
        "properties": {
            "action": {
                "type": "string",
                "description": "Action to perform.",
                "enum": ["create", "check", "uncheck", "list", "clear"],
            },
            "items": {
                "type": "array",
                "items": {"type": "string"},
                "description": "List of task descriptions (used with 'create' action).",
            },
            "index": {
                "type": "integer",
                "description": "Task index (0-based, used with 'check'/'uncheck' actions).",
            },
        },
        "required": ["action"],
    }

    def __init__(self):
        self._tasks: list[dict] = []  # [{"text": str, "done": bool}]

    async def execute(self, params: dict) -> str:
        try:
            action = params["action"]

            if action == "create":
                items = params.get("items", [])
                if not items:
                    return "Error: No items provided for create action."
                for item in items:
                    self._tasks.append({"text": item, "done": False})
                return f"Created {len(items)} task(s). Total: {len(self._tasks)}."

            elif action == "check":
                index = params.get("index")
                if index is None:
                    return "Error: No index provided for check action."
                if index < 0 or index >= len(self._tasks):
                    return f"Error: Index {index} out of range (0-{len(self._tasks) - 1})."
                self._tasks[index]["done"] = True
                return f"Checked: {self._tasks[index]['text']}"

            elif action == "uncheck":
                index = params.get("index")
                if index is None:
                    return "Error: No index provided for uncheck action."
                if index < 0 or index >= len(self._tasks):
                    return f"Error: Index {index} out of range (0-{len(self._tasks) - 1})."
                self._tasks[index]["done"] = False
                return f"Unchecked: {self._tasks[index]['text']}"

            elif action == "list":
                if not self._tasks:
                    return "No tasks."
                lines = []
                for i, task in enumerate(self._tasks):
                    mark = "[x]" if task["done"] else "[ ]"
                    lines.append(f"{i}: {mark} {task['text']}")
                return "\n".join(lines)

            elif action == "clear":
                count = len(self._tasks)
                self._tasks.clear()
                return f"Cleared {count} task(s)."

            else:
                return f"Error: Unknown action '{action}'."
        except Exception as e:
            return f"Error in todo_list: {e}"
