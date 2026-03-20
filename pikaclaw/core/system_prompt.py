"""System prompt builder for PikaClaw agents."""
from __future__ import annotations
import os
import platform
import subprocess
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pikaclaw.agents.base import AgentDefinition
    from pikaclaw.core.agent_loop import LoopState
    from pikaclaw.config.schema import PikaClawConfig

BASE_PROMPT = """You are PikaClaw, a self-hosted AI coding agent. You help users with software engineering tasks by reading, writing, and executing code.

## Environment
- Working directory: {cwd}
- OS: {os_info}
- Git branch: {git_branch}
- Date: {date}

## Available Tools
You have access to these tools. Use them to accomplish tasks:
- Read: Read file contents (params: file_path, start_line?, end_line?)
- Write: Create/overwrite files (params: file_path, content)
- Edit: Search-and-replace in files (params: file_path, old_text, new_text)
- Bash: Execute shell commands (params: command, timeout?)
- Grep: Regex search across files (params: pattern, path?, include?)
- Glob: Find files by pattern (params: pattern, path?)
- Git: Git operations (params: subcommand, args?)
- WebSearch: Search the web (params: query)
- WebFetch: Fetch URL content (params: url)
- TodoList: Manage task checklist (params: action, items?, index?)
- AskUser: Ask the user a question (params: question, options?)
- AgentSpawn: Spawn a sub-agent (params: agent, prompt)
- Remember: Store to memory (params: key, value, category?)
- Recall: Search memory (params: query, category?)
- Undo: Undo last file change (no params)
- Redo: Redo last undone change (no params)

## Workflow
1. UNDERSTAND: Read the request carefully
2. EXPLORE: Read relevant files, search codebase
3. PLAN: Think through the approach
4. IMPLEMENT: Make changes with minimal diffs
5. VERIFY: Run tests, check for errors
6. COMPLETE: Summarize what was done

## Code Standards
- Follow existing code patterns and style
- Add type hints to new code
- Handle errors gracefully
- Write minimal, focused diffs
- Never leave TODO comments in production code

## Security Rules
- NEVER read or output .env files, API keys, or credentials
- NEVER execute rm -rf / or destructive system commands
- NEVER bypass security checks
- NEVER modify files in pikaclaw/security/
- Always sanitize secrets from output
- Ask permission before destructive operations

## Communication
- Be direct and concise
- Show code, don't just describe it
- Report errors honestly
- Ask when requirements are unclear
"""


class SystemPromptBuilder:
    """Builds complete system prompt for agent loop."""

    def build(self, agent: AgentDefinition, state: LoopState, config: PikaClawConfig) -> str:
        prompt = BASE_PROMPT.format(
            cwd=os.getcwd(),
            os_info=f"{platform.system()} {platform.release()}",
            git_branch=self._get_git_branch(),
            date=self._get_date(),
        )

        # Agent-specific prompt
        prompt += f"\n\n## Active Agent: {agent.display_name} {agent.icon}\n{agent.system_prompt}\n"

        # Load PIKACLAW.md if exists
        pikaclaw_md = self._load_pikaclaw_md()
        if pikaclaw_md:
            prompt += f"\n## Project Instructions (PIKACLAW.md)\n{pikaclaw_md[:4000]}\n"

        # Tool restrictions
        if agent.denied_tools:
            prompt += f"\n## RESTRICTED: You CANNOT use these tools: {', '.join(agent.denied_tools)}\n"
        if not agent.can_write_files:
            prompt += "\n## RESTRICTION: You are in READ-ONLY mode. You CANNOT create, write, or edit files.\n"
        if not agent.can_execute_bash:
            prompt += "\n## RESTRICTION: You CANNOT execute shell commands.\n"

        return prompt

    def _get_git_branch(self) -> str:
        try:
            result = subprocess.run(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                capture_output=True, text=True, timeout=5,
            )
            return result.stdout.strip() if result.returncode == 0 else "N/A"
        except Exception:
            return "N/A"

    def _get_date(self) -> str:
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M")

    def _load_pikaclaw_md(self) -> str:
        for name in ["PIKACLAW.md", ".pikaclaw/PIKACLAW.md"]:
            p = Path(name)
            if p.exists():
                try:
                    return p.read_text()
                except Exception:
                    pass
        return ""
