"""Hook system for pre/post tool execution."""
from __future__ import annotations
from typing import Callable


class HookSystem:
    """Manages pre/post hooks for tool execution."""

    def __init__(self):
        self._pre_hooks: list[Callable] = []
        self._post_hooks: list[Callable] = []

    def register_pre_hook(self, hook: Callable):
        self._pre_hooks.append(hook)

    def register_post_hook(self, hook: Callable):
        self._post_hooks.append(hook)

    async def run_pre_hooks(self, tool_name: str, tool_input: dict) -> dict | None:
        """Run pre-hooks. Return modified input or None to block."""
        for hook in self._pre_hooks:
            result = hook(tool_name, tool_input)
            if result is None:
                return None  # Hook blocked the call
            if isinstance(result, dict):
                tool_input = result
        return tool_input

    async def run_post_hooks(self, tool_name: str, tool_input: dict, output: str) -> str:
        """Run post-hooks. Return potentially modified output."""
        for hook in self._post_hooks:
            result = hook(tool_name, tool_input, output)
            if isinstance(result, str):
                output = result
        return output
