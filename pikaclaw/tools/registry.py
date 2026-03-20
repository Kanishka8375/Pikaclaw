"""Tool registry — auto-discovers and registers all builtin tools."""
from __future__ import annotations
from pikaclaw.tools.builtin.read import ReadTool
from pikaclaw.tools.builtin.write import WriteTool
from pikaclaw.tools.builtin.edit import EditTool
from pikaclaw.tools.builtin.bash import BashTool
from pikaclaw.tools.builtin.grep import GrepTool
from pikaclaw.tools.builtin.glob_tool import GlobTool
from pikaclaw.tools.builtin.git import GitTool
from pikaclaw.tools.builtin.web_search import WebSearchTool
from pikaclaw.tools.builtin.web_fetch import WebFetchTool
from pikaclaw.tools.builtin.todo_list import TodoListTool
from pikaclaw.tools.builtin.ask_user import AskUserTool
from pikaclaw.tools.builtin.agent_spawn import AgentSpawnTool
from pikaclaw.tools.builtin.remember import RememberTool
from pikaclaw.tools.builtin.recall import RecallTool
from pikaclaw.tools.builtin.undo import UndoTool
from pikaclaw.tools.builtin.redo import RedoTool
from pikaclaw.tools.builtin.screenshot import ScreenshotTool
from pikaclaw.tools.builtin.mcp import MCPTool
from pikaclaw.tools.builtin.world_model import WorldModelTool
from pikaclaw.tools.builtin.lsp import LSPTool


class CheckpointManager:
    """Tracks file changes for undo/redo."""

    def __init__(self):
        self.undo_stack: list[dict] = []  # [{"file_path": str, "old_content": str, "new_content": str}]
        self.redo_stack: list[dict] = []

    def save(self, file_path: str, old_content: str, new_content: str):
        self.undo_stack.append({"file_path": file_path, "old_content": old_content, "new_content": new_content})
        self.redo_stack.clear()

    def undo(self) -> str | None:
        if not self.undo_stack:
            return None
        cp = self.undo_stack.pop()
        self.redo_stack.append(cp)
        from pathlib import Path
        Path(cp["file_path"]).write_text(cp["old_content"])
        return cp["file_path"]

    def redo(self) -> str | None:
        if not self.redo_stack:
            return None
        cp = self.redo_stack.pop()
        self.undo_stack.append(cp)
        from pathlib import Path
        Path(cp["file_path"]).write_text(cp["new_content"])
        return cp["file_path"]


class ToolRegistry:
    """Registry of all available tools."""

    def __init__(self):
        self._tools: dict[str, object] = {}
        self.checkpoint = CheckpointManager()
        self._register_builtins()

    def _register_builtins(self):
        tools = [
            ReadTool(), WriteTool(self.checkpoint), EditTool(self.checkpoint),
            BashTool(), GrepTool(), GlobTool(), GitTool(),
            WebSearchTool(), WebFetchTool(), TodoListTool(),
            AskUserTool(), AgentSpawnTool(), RememberTool(), RecallTool(),
            UndoTool(self.checkpoint), RedoTool(self.checkpoint),
            ScreenshotTool(), MCPTool(), WorldModelTool(), LSPTool(),
        ]
        for tool in tools:
            self._tools[tool.name] = tool

    def get(self, name: str):
        return self._tools.get(name)

    def list_tools(self) -> list[dict]:
        return [{"name": t.name, "description": t.description, "parameters": t.parameters} for t in self._tools.values()]

    def get_tool_definitions(self, format: str = "openai") -> list[dict]:
        """Get tool definitions in OpenAI or Anthropic format."""
        if format == "anthropic":
            return [
                {"name": t.name, "description": t.description, "input_schema": t.parameters}
                for t in self._tools.values()
            ]
        # OpenAI format
        return [
            {"type": "function", "function": {"name": t.name, "description": t.description, "parameters": t.parameters}}
            for t in self._tools.values()
        ]
