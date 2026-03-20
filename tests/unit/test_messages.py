"""Tests for all PikaClaw message types."""
from __future__ import annotations

import pytest

from pikaclaw.core.messages import (
    AgentSwitchMessage,
    CompactMessage,
    DoneMessage,
    ErrorMessage,
    PermissionRequest,
    StatusMessage,
    TextMessage,
    ThinkingMessage,
    ToolCallMessage,
    ToolResultMessage,
)


# ---------------------------------------------------------------------------
# TextMessage
# ---------------------------------------------------------------------------

class TestTextMessage:
    def test_default_text_empty(self):
        msg = TextMessage()
        assert msg.text == ""

    def test_default_model_empty(self):
        msg = TextMessage()
        assert msg.model == ""

    def test_type_field(self):
        msg = TextMessage()
        assert msg.type == "text"

    def test_with_values(self):
        msg = TextMessage(text="hello", model="gpt-4")
        assert msg.text == "hello"
        assert msg.model == "gpt-4"

    def test_type_unchanged_after_construction(self):
        msg = TextMessage(text="x")
        assert msg.type == "text"


# ---------------------------------------------------------------------------
# ThinkingMessage
# ---------------------------------------------------------------------------

class TestThinkingMessage:
    def test_default_text_empty(self):
        msg = ThinkingMessage()
        assert msg.text == ""

    def test_type_field(self):
        msg = ThinkingMessage()
        assert msg.type == "thinking"

    def test_with_text(self):
        msg = ThinkingMessage(text="analyzing code")
        assert msg.text == "analyzing code"


# ---------------------------------------------------------------------------
# ToolCallMessage
# ---------------------------------------------------------------------------

class TestToolCallMessage:
    def test_default_tool_empty(self):
        msg = ToolCallMessage()
        assert msg.tool == ""

    def test_default_input_empty_dict(self):
        msg = ToolCallMessage()
        assert msg.input == {}

    def test_default_call_id_empty(self):
        msg = ToolCallMessage()
        assert msg.call_id == ""

    def test_type_field(self):
        msg = ToolCallMessage()
        assert msg.type == "tool_call"

    def test_with_dict_input(self):
        data = {"path": "/tmp/file.py", "content": "print('hi')"}
        msg = ToolCallMessage(tool="Write", input=data, call_id="tc_123")
        assert msg.tool == "Write"
        assert msg.input == data
        assert msg.call_id == "tc_123"

    def test_input_is_mutable_dict(self):
        msg1 = ToolCallMessage()
        msg2 = ToolCallMessage()
        msg1.input["key"] = "val"
        assert "key" not in msg2.input


# ---------------------------------------------------------------------------
# ToolResultMessage
# ---------------------------------------------------------------------------

class TestToolResultMessage:
    def test_default_tool_empty(self):
        msg = ToolResultMessage()
        assert msg.tool == ""

    def test_default_result_empty(self):
        msg = ToolResultMessage()
        assert msg.result == ""

    def test_default_is_error_false(self):
        msg = ToolResultMessage()
        assert msg.is_error is False

    def test_default_call_id_empty(self):
        msg = ToolResultMessage()
        assert msg.call_id == ""

    def test_type_field(self):
        msg = ToolResultMessage()
        assert msg.type == "tool_result"

    def test_with_error(self):
        msg = ToolResultMessage(tool="Bash", result="command not found", is_error=True)
        assert msg.is_error is True
        assert msg.result == "command not found"

    def test_with_success(self):
        msg = ToolResultMessage(tool="Read", result="file contents here", is_error=False)
        assert msg.is_error is False


# ---------------------------------------------------------------------------
# PermissionRequest
# ---------------------------------------------------------------------------

class TestPermissionRequest:
    def test_default_tool_empty(self):
        msg = PermissionRequest()
        assert msg.tool == ""

    def test_default_input_empty_dict(self):
        msg = PermissionRequest()
        assert msg.input == {}

    def test_default_request_id_empty(self):
        msg = PermissionRequest()
        assert msg.request_id == ""

    def test_type_field(self):
        msg = PermissionRequest()
        assert msg.type == "permission_request"

    def test_with_values(self):
        msg = PermissionRequest(tool="Bash", input={"command": "rm -rf /"}, request_id="pr_1")
        assert msg.tool == "Bash"
        assert msg.input["command"] == "rm -rf /"
        assert msg.request_id == "pr_1"

    def test_input_is_mutable_dict(self):
        msg1 = PermissionRequest()
        msg2 = PermissionRequest()
        msg1.input["x"] = 1
        assert "x" not in msg2.input


# ---------------------------------------------------------------------------
# DoneMessage
# ---------------------------------------------------------------------------

class TestDoneMessage:
    def test_default_turns_zero(self):
        msg = DoneMessage()
        assert msg.turns == 0

    def test_default_tokens_zero(self):
        msg = DoneMessage()
        assert msg.tokens == 0

    def test_default_cost_zero(self):
        msg = DoneMessage()
        assert msg.cost == 0.0

    def test_type_field(self):
        msg = DoneMessage()
        assert msg.type == "done"

    def test_with_stats(self):
        msg = DoneMessage(turns=5, tokens=12000, cost=0.042)
        assert msg.turns == 5
        assert msg.tokens == 12000
        assert msg.cost == pytest.approx(0.042)


# ---------------------------------------------------------------------------
# ErrorMessage
# ---------------------------------------------------------------------------

class TestErrorMessage:
    def test_default_error_empty(self):
        msg = ErrorMessage()
        assert msg.error == ""

    def test_type_field(self):
        msg = ErrorMessage()
        assert msg.type == "error"

    def test_with_error_text(self):
        msg = ErrorMessage(error="something went wrong")
        assert msg.error == "something went wrong"


# ---------------------------------------------------------------------------
# AgentSwitchMessage
# ---------------------------------------------------------------------------

class TestAgentSwitchMessage:
    def test_default_from_agent_empty(self):
        msg = AgentSwitchMessage()
        assert msg.from_agent == ""

    def test_default_to_agent_empty(self):
        msg = AgentSwitchMessage()
        assert msg.to_agent == ""

    def test_type_field(self):
        msg = AgentSwitchMessage()
        assert msg.type == "agent_switch"

    def test_with_values(self):
        msg = AgentSwitchMessage(from_agent="build", to_agent="test")
        assert msg.from_agent == "build"
        assert msg.to_agent == "test"


# ---------------------------------------------------------------------------
# StatusMessage
# ---------------------------------------------------------------------------

class TestStatusMessage:
    def test_default_status_empty(self):
        msg = StatusMessage()
        assert msg.status == ""

    def test_type_field(self):
        msg = StatusMessage()
        assert msg.type == "status"

    def test_with_status(self):
        msg = StatusMessage(status="processing")
        assert msg.status == "processing"


# ---------------------------------------------------------------------------
# CompactMessage
# ---------------------------------------------------------------------------

class TestCompactMessage:
    def test_default_original_tokens_zero(self):
        msg = CompactMessage()
        assert msg.original_tokens == 0

    def test_default_compacted_tokens_zero(self):
        msg = CompactMessage()
        assert msg.compacted_tokens == 0

    def test_type_field(self):
        msg = CompactMessage()
        assert msg.type == "compact"

    def test_with_values(self):
        msg = CompactMessage(original_tokens=50000, compacted_tokens=5000)
        assert msg.original_tokens == 50000
        assert msg.compacted_tokens == 5000


# ---------------------------------------------------------------------------
# Cross-cutting tests
# ---------------------------------------------------------------------------

class TestAllMessageTypes:
    @pytest.mark.parametrize(
        "cls,expected_type",
        [
            (TextMessage, "text"),
            (ThinkingMessage, "thinking"),
            (ToolCallMessage, "tool_call"),
            (ToolResultMessage, "tool_result"),
            (PermissionRequest, "permission_request"),
            (DoneMessage, "done"),
            (ErrorMessage, "error"),
            (AgentSwitchMessage, "agent_switch"),
            (StatusMessage, "status"),
            (CompactMessage, "compact"),
        ],
    )
    def test_type_field_correct(self, cls, expected_type):
        msg = cls()
        assert msg.type == expected_type

    @pytest.mark.parametrize(
        "cls",
        [
            TextMessage,
            ThinkingMessage,
            ToolCallMessage,
            ToolResultMessage,
            PermissionRequest,
            DoneMessage,
            ErrorMessage,
            AgentSwitchMessage,
            StatusMessage,
            CompactMessage,
        ],
    )
    def test_all_types_are_dataclasses(self, cls):
        import dataclasses
        assert dataclasses.is_dataclass(cls)
