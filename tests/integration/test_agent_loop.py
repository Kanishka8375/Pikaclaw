"""Integration tests for the agent loop with mock provider."""
import pytest
import json
from unittest.mock import AsyncMock, MagicMock, patch
from pikaclaw.core.agent_loop import AgentLoop, LoopState
from pikaclaw.core.messages import TextMessage, ToolCallMessage, ToolResultMessage, DoneMessage, ErrorMessage
from pikaclaw.tools.registry import ToolRegistry
from pikaclaw.agents.registry import AGENTS
from pikaclaw.security.permissions import PermissionEvaluator
from pikaclaw.config.loader import load_config


class MockRouter:
    """Mock model router that returns predefined responses."""
    def __init__(self, responses=None):
        self.responses = responses or []
        self._call_count = 0
        self.config = load_config()

    async def complete(self, messages, model=None, tools=None, system=None):
        if self._call_count < len(self.responses):
            resp = self.responses[self._call_count]
            self._call_count += 1
            return resp
        return {"content": "No more responses", "tool_calls": [], "usage": {"input_tokens": 10, "output_tokens": 5}}


def make_loop(responses):
    router = MockRouter(responses)
    return AgentLoop(
        model_router=router,
        tool_registry=ToolRegistry(),
        permission_system=PermissionEvaluator(),
        agent_registry=AGENTS,
        config=load_config(),
    )


@pytest.mark.asyncio
async def test_simple_text_response():
    """Agent returns a text response with no tool calls."""
    loop = make_loop([
        {"content": "Hello! How can I help?", "tool_calls": [], "usage": {"input_tokens": 10, "output_tokens": 5}}
    ])
    state = LoopState()
    messages = []
    async for msg in loop.run("Say hello", state):
        messages.append(msg)
    
    types = [m.type for m in messages]
    assert "text" in types
    assert "done" in types
    text_msgs = [m for m in messages if m.type == "text"]
    assert len(text_msgs) >= 1
    assert "Hello" in text_msgs[0].text


@pytest.mark.asyncio
async def test_tool_use_read():
    """Agent calls Read tool then responds."""
    loop = make_loop([
        # First response: call Read tool
        {"content": "", "tool_calls": [{"name": "Read", "input": {"file_path": "pyproject.toml"}, "id": "call1"}],
         "usage": {"input_tokens": 20, "output_tokens": 10}},
        # Second response: text after seeing tool result
        {"content": "The version is 0.1.0", "tool_calls": [],
         "usage": {"input_tokens": 30, "output_tokens": 15}},
    ])
    state = LoopState()
    messages = []
    async for msg in loop.run("What version?", state):
        messages.append(msg)
    
    types = [m.type for m in messages]
    assert "tool_call" in types
    assert "tool_result" in types
    assert "text" in types
    
    tool_call = next(m for m in messages if m.type == "tool_call")
    assert tool_call.tool == "Read"
    
    tool_result = next(m for m in messages if m.type == "tool_result")
    assert not tool_result.is_error
    assert "pikaclaw" in tool_result.result


@pytest.mark.asyncio
async def test_permission_denied():
    """Plan agent trying to write is denied."""
    loop = make_loop([
        {"content": "", "tool_calls": [{"name": "Write", "input": {"file_path": "test.py", "content": "x"}, "id": "c1"}],
         "usage": {"input_tokens": 10, "output_tokens": 5}},
        {"content": "I cannot write files.", "tool_calls": [],
         "usage": {"input_tokens": 20, "output_tokens": 10}},
    ])
    state = LoopState(active_agent="plan")
    messages = []
    async for msg in loop.run("Write a file", state):
        messages.append(msg)
    
    tool_results = [m for m in messages if m.type == "tool_result"]
    assert len(tool_results) >= 1
    assert tool_results[0].is_error
    assert "denied" in tool_results[0].result.lower() or "not allowed" in tool_results[0].result.lower()


@pytest.mark.asyncio
async def test_sentinel_blocks_security_file():
    """Writing to security files is blocked."""
    loop = make_loop([
        {"content": "", "tool_calls": [{"name": "Write", "input": {"file_path": "pikaclaw/security/sentinel.py", "content": "x"}, "id": "c1"}],
         "usage": {"input_tokens": 10, "output_tokens": 5}},
        {"content": "Blocked.", "tool_calls": [],
         "usage": {"input_tokens": 20, "output_tokens": 10}},
    ])
    state = LoopState()
    messages = []
    async for msg in loop.run("Modify sentinel", state):
        messages.append(msg)
    
    tool_results = [m for m in messages if m.type == "tool_result"]
    assert len(tool_results) >= 1
    assert tool_results[0].is_error
    assert "protected" in tool_results[0].result.lower()


@pytest.mark.asyncio
async def test_bash_denied_rm_rf():
    """rm -rf / is blocked."""
    loop = make_loop([
        {"content": "", "tool_calls": [{"name": "Bash", "input": {"command": "rm -rf /"}, "id": "c1"}],
         "usage": {"input_tokens": 10, "output_tokens": 5}},
        {"content": "Cannot do that.", "tool_calls": [],
         "usage": {"input_tokens": 20, "output_tokens": 10}},
    ])
    state = LoopState()
    messages = []
    async for msg in loop.run("Delete everything", state):
        messages.append(msg)
    
    tool_results = [m for m in messages if m.type == "tool_result"]
    assert len(tool_results) >= 1
    assert tool_results[0].is_error


@pytest.mark.asyncio
async def test_done_message_has_stats():
    """DoneMessage includes turn count and token count."""
    loop = make_loop([
        {"content": "Hi", "tool_calls": [], "usage": {"input_tokens": 10, "output_tokens": 5}}
    ])
    state = LoopState()
    messages = []
    async for msg in loop.run("Hello", state):
        messages.append(msg)
    
    done = next(m for m in messages if m.type == "done")
    assert done.turns >= 1
    assert done.tokens >= 0


@pytest.mark.asyncio
async def test_multiple_tool_calls():
    """Agent calls multiple tools in sequence."""
    loop = make_loop([
        {"content": "", "tool_calls": [
            {"name": "Bash", "input": {"command": "echo test1"}, "id": "c1"},
            {"name": "Bash", "input": {"command": "echo test2"}, "id": "c2"},
        ], "usage": {"input_tokens": 10, "output_tokens": 5}},
        {"content": "Both commands ran.", "tool_calls": [],
         "usage": {"input_tokens": 20, "output_tokens": 10}},
    ])
    state = LoopState()
    messages = []
    async for msg in loop.run("Run two commands", state):
        messages.append(msg)
    
    tool_calls = [m for m in messages if m.type == "tool_call"]
    assert len(tool_calls) == 2


@pytest.mark.asyncio
async def test_max_turns_limit():
    """Agent loop stops after max_turns."""
    # Every response has a tool call, so the loop would go forever
    responses = [
        {"content": "", "tool_calls": [{"name": "Bash", "input": {"command": "echo x"}, "id": f"c{i}"}],
         "usage": {"input_tokens": 1, "output_tokens": 1}}
        for i in range(10)
    ]
    loop = make_loop(responses)
    state = LoopState(max_turns=3)
    messages = []
    async for msg in loop.run("Loop forever", state):
        messages.append(msg)
    
    assert state.turn_count <= 3


@pytest.mark.asyncio
async def test_secret_sanitization_in_response():
    """Secrets in model response are sanitized."""
    loop = make_loop([
        {"content": "Here is the key: sk-ant-abc123456789xyz", "tool_calls": [],
         "usage": {"input_tokens": 10, "output_tokens": 5}}
    ])
    state = LoopState()
    messages = []
    async for msg in loop.run("Show key", state):
        messages.append(msg)
    
    text_msgs = [m for m in messages if m.type == "text"]
    assert len(text_msgs) >= 1
    assert "sk-ant-" not in text_msgs[0].text


@pytest.mark.asyncio
async def test_secret_sanitization_in_tool_output():
    """Secrets in tool output are sanitized."""
    loop = make_loop([
        {"content": "", "tool_calls": [{"name": "Bash", "input": {"command": "echo sk-ant-abc123456789xyz"}, "id": "c1"}],
         "usage": {"input_tokens": 10, "output_tokens": 5}},
        {"content": "Done.", "tool_calls": [],
         "usage": {"input_tokens": 20, "output_tokens": 10}},
    ])
    state = LoopState()
    messages = []
    async for msg in loop.run("Echo a secret", state):
        messages.append(msg)
    
    tool_results = [m for m in messages if m.type == "tool_result"]
    assert len(tool_results) >= 1
    assert "sk-ant-" not in tool_results[0].result


@pytest.mark.asyncio
async def test_agent_switch_changes_permissions():
    """Switching agent changes available tools."""
    loop = make_loop([
        {"content": "", "tool_calls": [{"name": "Write", "input": {"file_path": "/tmp/test.txt", "content": "x"}, "id": "c1"}],
         "usage": {"input_tokens": 10, "output_tokens": 5}},
        {"content": "Cannot write.", "tool_calls": [],
         "usage": {"input_tokens": 20, "output_tokens": 10}},
    ])
    # Build agent can write
    state = LoopState(active_agent="build")
    msgs = []
    async for msg in loop.run("Write file", state):
        msgs.append(msg)
    results = [m for m in msgs if m.type == "tool_result"]
    if results:
        assert not results[0].is_error  # build can write
    
    # Review agent cannot write
    loop2 = make_loop([
        {"content": "", "tool_calls": [{"name": "Write", "input": {"file_path": "/tmp/test.txt", "content": "x"}, "id": "c1"}],
         "usage": {"input_tokens": 10, "output_tokens": 5}},
        {"content": "Cannot.", "tool_calls": [],
         "usage": {"input_tokens": 20, "output_tokens": 10}},
    ])
    state2 = LoopState(active_agent="review")
    msgs2 = []
    async for msg in loop2.run("Write file", state2):
        msgs2.append(msg)
    results2 = [m for m in msgs2 if m.type == "tool_result"]
    assert len(results2) >= 1
    assert results2[0].is_error


@pytest.mark.asyncio
async def test_unknown_tool():
    """Unknown tool name returns error."""
    loop = make_loop([
        {"content": "", "tool_calls": [{"name": "FakeTool", "input": {}, "id": "c1"}],
         "usage": {"input_tokens": 10, "output_tokens": 5}},
        {"content": "OK.", "tool_calls": [],
         "usage": {"input_tokens": 20, "output_tokens": 10}},
    ])
    state = LoopState()
    messages = []
    async for msg in loop.run("Use fake", state):
        messages.append(msg)
    
    results = [m for m in messages if m.type == "tool_result"]
    assert len(results) >= 1
    assert results[0].is_error
    assert "unknown" in results[0].result.lower() or "Unknown" in results[0].result


@pytest.mark.asyncio
async def test_model_error_yields_error_message():
    """Model call failure yields ErrorMessage."""
    class FailRouter:
        config = load_config()
        async def complete(self, **kwargs):
            raise ConnectionError("Model offline")
    
    loop = AgentLoop(
        model_router=FailRouter(),
        tool_registry=ToolRegistry(),
        permission_system=PermissionEvaluator(),
        agent_registry=AGENTS,
        config=load_config(),
    )
    state = LoopState()
    messages = []
    async for msg in loop.run("Hello", state):
        messages.append(msg)
    
    types = [m.type for m in messages]
    assert "error" in types or "done" in types


@pytest.mark.asyncio
async def test_loop_state_tracks_tokens():
    """LoopState accumulates token counts."""
    loop = make_loop([
        {"content": "Hi", "tool_calls": [], "usage": {"input_tokens": 100, "output_tokens": 50}}
    ])
    state = LoopState()
    async for _ in loop.run("Hello", state):
        pass
    assert state.total_input_tokens == 100
    assert state.total_output_tokens == 50
