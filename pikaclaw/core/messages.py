"""Message types for the PikaClaw agent loop."""
from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class TextMessage:
    text: str = ""
    model: str = ""
    type: str = "text"


@dataclass
class ThinkingMessage:
    text: str = ""
    type: str = "thinking"


@dataclass
class ToolCallMessage:
    tool: str = ""
    input: dict = field(default_factory=dict)
    call_id: str = ""
    type: str = "tool_call"


@dataclass
class ToolResultMessage:
    tool: str = ""
    result: str = ""
    is_error: bool = False
    call_id: str = ""
    type: str = "tool_result"


@dataclass
class PermissionRequest:
    tool: str = ""
    input: dict = field(default_factory=dict)
    request_id: str = ""
    type: str = "permission_request"


@dataclass
class DoneMessage:
    turns: int = 0
    tokens: int = 0
    cost: float = 0.0
    type: str = "done"


@dataclass
class ErrorMessage:
    error: str = ""
    type: str = "error"


@dataclass
class AgentSwitchMessage:
    from_agent: str = ""
    to_agent: str = ""
    type: str = "agent_switch"


@dataclass
class StatusMessage:
    status: str = ""
    type: str = "status"


@dataclass
class CompactMessage:
    original_tokens: int = 0
    compacted_tokens: int = 0
    type: str = "compact"
