"""Agent definition dataclass."""
from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class AgentDefinition:
    """Defines an agent's capabilities, permissions, and behavior."""
    name: str
    display_name: str
    description: str
    icon: str
    mode: str  # "primary" | "specialist" | "system"
    system_prompt: str
    preferred_model: str | None = None
    preferred_local: str | None = None
    temperature: float = 0.0
    max_turns: int = 250
    allowed_tools: list[str] = field(default_factory=list)
    denied_tools: list[str] = field(default_factory=list)
    can_write_files: bool = True
    can_execute_bash: bool = True
    can_access_network: bool = True
    can_modify_git: bool = True
    can_spawn_agents: bool = True
    skills: list[str] = field(default_factory=list)
    auto_load_context: bool = True
