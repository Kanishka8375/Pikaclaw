"""Permission evaluator — controls what tools agents can use."""
from __future__ import annotations
import re
import fnmatch
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pikaclaw.agents.base import AgentDefinition

# Patterns that are ALWAYS denied regardless of agent
DENY_PATTERNS = [
    r"rm\s+(-[rf]+\s+)*(/|/\*)",
    r"rm\s+-rf\s+/",
    r"chmod\s+(-R\s+)?777",
    r"mkfs\.",
    r">\s*/dev/sd",
    r"dd\s+if=",
    r"curl\s+.*\|\s*(sh|bash)",
    r"wget\s+.*\|\s*(sh|bash)",
    r"nc\s+-[el]",
    r"ncat\s+-[el]",
    r":\(\)\s*\{\s*:\|:&\s*\}\s*;:",
    r"python.*-c.*exec\(",
    r">\s*/etc/",
]

_compiled_deny = [re.compile(p, re.IGNORECASE) for p in DENY_PATTERNS]


class PermissionEvaluator:
    """Evaluates whether a tool call should be allowed, denied, or asked."""

    def __init__(self, config=None):
        self.config = config
        self._extra_denied: list[str] = []
        if config and hasattr(config, 'security'):
            self._extra_denied = config.security.denied_commands

    def evaluate(self, tool_name: str, tool_input: dict, agent: AgentDefinition | None) -> str:
        """Returns 'allow', 'deny', or 'ask'."""
        # Check agent permission constraints
        if agent:
            if tool_name in ("Write", "Edit") and not agent.can_write_files:
                return "deny"
            if tool_name == "Bash" and not agent.can_execute_bash:
                return "deny"
            if tool_name == "Git" and not agent.can_modify_git:
                # Allow read-only git commands
                subcmd = tool_input.get("subcommand", "")
                if subcmd not in ("status", "diff", "log", "show", "branch"):
                    return "deny"
            if tool_name in agent.denied_tools:
                return "deny"

        # Check Bash commands against deny patterns
        if tool_name == "Bash":
            command = tool_input.get("command", "")
            for pattern in _compiled_deny:
                if pattern.search(command):
                    return "deny"
            # Check extra denied commands from config
            for denied in self._extra_denied:
                if denied in command:
                    return "deny"

        return "allow"

    def check_file_permission(self, file_path: str, agent: AgentDefinition | None, protected_paths: list[str] | None = None) -> str:
        """Check if writing to a file is allowed."""
        if agent and not agent.can_write_files:
            return "deny"
        if protected_paths:
            for pattern in protected_paths:
                if fnmatch.fnmatch(file_path, pattern):
                    return "deny"
        return "allow"
