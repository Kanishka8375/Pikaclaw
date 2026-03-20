"""Tests for the tool registry and all builtin tools."""
import pytest
import asyncio
import os
import tempfile
import shutil
from pikaclaw.tools.registry import ToolRegistry, CheckpointManager


@pytest.fixture
def registry():
    return ToolRegistry()


# ============================================================
# Registry tests
# ============================================================

def test_registry_has_20_tools(registry):
    assert len(registry._tools) == 20


def test_registry_get_existing(registry):
    assert registry.get("Read") is not None


def test_registry_get_missing(registry):
    assert registry.get("NonExistent") is None


def test_registry_list_tools(registry):
    tools = registry.list_tools()
    assert len(tools) == 20
    assert all("name" in t and "description" in t and "parameters" in t for t in tools)


def test_registry_list_tools_names(registry):
    names = {t["name"] for t in registry.list_tools()}
    expected = {
        "Read", "Write", "Edit", "Bash", "Grep", "Glob", "Git",
        "WebSearch", "WebFetch", "TodoList", "AskUser", "AgentSpawn",
        "Remember", "Recall", "Undo", "Redo", "Screenshot", "MCP",
        "WorldModel", "LSP",
    }
    assert names == expected


def test_tool_definitions_openai(registry):
    defs = registry.get_tool_definitions("openai")
    assert len(defs) == 20
    assert all(d["type"] == "function" for d in defs)


def test_tool_definitions_openai_structure(registry):
    defs = registry.get_tool_definitions("openai")
    for d in defs:
        assert "function" in d
        assert "name" in d["function"]
        assert "description" in d["function"]
        assert "parameters" in d["function"]


def test_tool_definitions_anthropic(registry):
    defs = registry.get_tool_definitions("anthropic")
    assert len(defs) == 20
    assert all("input_schema" in d for d in defs)


def test_tool_definitions_anthropic_has_name(registry):
    defs = registry.get_tool_definitions("anthropic")
    assert all("name" in d for d in defs)


def test_tool_definitions_anthropic_has_description(registry):
    defs = registry.get_tool_definitions("anthropic")
    assert all("description" in d for d in defs)


# ============================================================
# CheckpointManager tests
# ============================================================

def test_checkpoint_save_and_undo():
    cm = CheckpointManager()
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        f.write("new content")
        path = f.name
    cm.save(path, "old content", "new content")
    restored = cm.undo()
    assert restored == path
    assert open(path).read() == "old content"
    os.unlink(path)


def test_checkpoint_redo():
    cm = CheckpointManager()
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        f.write("new content")
        path = f.name
    cm.save(path, "old content", "new content")
    cm.undo()
    redone = cm.redo()
    assert redone == path
    assert open(path).read() == "new content"
    os.unlink(path)


def test_checkpoint_undo_empty():
    cm = CheckpointManager()
    assert cm.undo() is None


def test_checkpoint_redo_empty():
    cm = CheckpointManager()
    assert cm.redo() is None


def test_checkpoint_multiple_saves():
    cm = CheckpointManager()
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        f.write("v3")
        path = f.name
    cm.save(path, "v1", "v2")
    cm.save(path, "v2", "v3")
    # Undo should restore v2
    cm.undo()
    assert open(path).read() == "v2"
    # Undo again should restore v1
    cm.undo()
    assert open(path).read() == "v1"
    os.unlink(path)


def test_checkpoint_redo_cleared_by_save():
    cm = CheckpointManager()
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        f.write("v2")
        path = f.name
    cm.save(path, "v1", "v2")
    cm.undo()
    # New save should clear redo stack
    cm.save(path, "v1", "v3")
    assert cm.redo() is None
    os.unlink(path)


def test_checkpoint_stacks_independent():
    cm = CheckpointManager()
    assert len(cm.undo_stack) == 0
    assert len(cm.redo_stack) == 0
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        f.write("data")
        path = f.name
    cm.save(path, "old", "new")
    assert len(cm.undo_stack) == 1
    assert len(cm.redo_stack) == 0
    cm.undo()
    assert len(cm.undo_stack) == 0
    assert len(cm.redo_stack) == 1
    os.unlink(path)


# ============================================================
# Individual tool tests
# ============================================================

@pytest.mark.asyncio
async def test_read_tool(registry):
    result = await registry.get("Read").execute({"file_path": "pyproject.toml"})
    assert "pikaclaw" in result.lower()
    assert len(result) > 50


@pytest.mark.asyncio
async def test_read_tool_nonexistent(registry):
    result = await registry.get("Read").execute({"file_path": "/tmp/nonexistent_file_xyz"})
    assert "error" in result.lower() or "not found" in result.lower()


@pytest.mark.asyncio
async def test_read_tool_directory(registry):
    result = await registry.get("Read").execute({"file_path": "pikaclaw"})
    assert "error" in result.lower() or "directory" in result.lower()


@pytest.mark.asyncio
async def test_read_tool_with_line_range(registry):
    result = await registry.get("Read").execute({
        "file_path": "pyproject.toml",
        "start_line": 1,
        "end_line": 3,
    })
    lines = result.strip().split("\n")
    assert len(lines) <= 3


@pytest.mark.asyncio
async def test_write_tool(registry):
    path = "/tmp/pk_write_test.txt"
    await registry.get("Write").execute({"file_path": path, "content": "test content"})
    assert os.path.exists(path)
    assert open(path).read() == "test content"
    os.unlink(path)


@pytest.mark.asyncio
async def test_write_creates_dirs(registry):
    path = "/tmp/pk_deep/nested/dir/test.txt"
    await registry.get("Write").execute({"file_path": path, "content": "deep"})
    assert open(path).read() == "deep"
    shutil.rmtree("/tmp/pk_deep")


@pytest.mark.asyncio
async def test_write_overwrites(registry):
    path = "/tmp/pk_write_overwrite.txt"
    await registry.get("Write").execute({"file_path": path, "content": "first"})
    await registry.get("Write").execute({"file_path": path, "content": "second"})
    assert open(path).read() == "second"
    os.unlink(path)


@pytest.mark.asyncio
async def test_write_returns_success(registry):
    path = "/tmp/pk_write_ret.txt"
    result = await registry.get("Write").execute({"file_path": path, "content": "abc"})
    assert "successfully" in result.lower() or "wrote" in result.lower()
    os.unlink(path)


@pytest.mark.asyncio
async def test_edit_tool(registry):
    path = "/tmp/pk_edit_test.txt"
    with open(path, "w") as f:
        f.write("hello old world")
    await registry.get("Edit").execute({
        "file_path": path,
        "old_text": "old",
        "new_text": "new",
    })
    assert "new" in open(path).read()
    os.unlink(path)


@pytest.mark.asyncio
async def test_edit_not_found(registry):
    path = "/tmp/pk_edit_nf.txt"
    with open(path, "w") as f:
        f.write("hello world")
    result = await registry.get("Edit").execute({
        "file_path": path,
        "old_text": "xyz_not_here",
        "new_text": "new",
    })
    assert "not found" in result.lower() or "error" in result.lower()
    os.unlink(path)


@pytest.mark.asyncio
async def test_edit_multiple_matches(registry):
    path = "/tmp/pk_edit_multi.txt"
    with open(path, "w") as f:
        f.write("foo foo foo")
    result = await registry.get("Edit").execute({
        "file_path": path,
        "old_text": "foo",
        "new_text": "bar",
    })
    assert "3 times" in result or "unique" in result.lower() or "error" in result.lower()
    os.unlink(path)


@pytest.mark.asyncio
async def test_edit_nonexistent_file(registry):
    result = await registry.get("Edit").execute({
        "file_path": "/tmp/pk_edit_missing_xyz.txt",
        "old_text": "a",
        "new_text": "b",
    })
    assert "error" in result.lower() or "not found" in result.lower()


@pytest.mark.asyncio
async def test_edit_saves_checkpoint(registry):
    path = "/tmp/pk_edit_cp.txt"
    with open(path, "w") as f:
        f.write("before")
    await registry.get("Edit").execute({
        "file_path": path,
        "old_text": "before",
        "new_text": "after",
    })
    # The registry checkpoint should have an entry
    assert len(registry.checkpoint.undo_stack) > 0
    os.unlink(path)


@pytest.mark.asyncio
async def test_bash_tool(registry):
    result = await registry.get("Bash").execute({"command": "echo hello_bash_test"})
    assert "hello_bash_test" in result


@pytest.mark.asyncio
async def test_bash_exit_code(registry):
    result = await registry.get("Bash").execute({"command": "exit 1"})
    assert "1" in result


@pytest.mark.asyncio
async def test_bash_stderr(registry):
    result = await registry.get("Bash").execute({"command": "echo err >&2"})
    assert "err" in result


@pytest.mark.asyncio
async def test_bash_multiline(registry):
    result = await registry.get("Bash").execute({"command": "echo line1 && echo line2"})
    assert "line1" in result
    assert "line2" in result


@pytest.mark.asyncio
async def test_grep_tool(registry):
    result = await registry.get("Grep").execute({"pattern": "class.*Tool", "path": "pikaclaw/tools/"})
    assert len(result) > 10


@pytest.mark.asyncio
async def test_grep_no_matches(registry):
    result = await registry.get("Grep").execute({"pattern": "xyzzy_nonexistent_123", "path": "pikaclaw/"})
    assert "no matches" in result.lower()


@pytest.mark.asyncio
async def test_glob_tool(registry):
    result = await registry.get("Glob").execute({"pattern": "pikaclaw/**/*.py"})
    assert "pikaclaw" in result


@pytest.mark.asyncio
async def test_glob_no_matches(registry):
    result = await registry.get("Glob").execute({"pattern": "**/*.xyzzy_nonexistent"})
    assert "no matching" in result.lower()


@pytest.mark.asyncio
async def test_glob_nonexistent_path(registry):
    result = await registry.get("Glob").execute({"pattern": "*.py", "path": "/tmp/nonexistent_dir_xyz"})
    assert "error" in result.lower() or "not found" in result.lower()


@pytest.mark.asyncio
async def test_git_tool(registry):
    result = await registry.get("Git").execute({"subcommand": "status"})
    assert result is not None and len(result) > 0


@pytest.mark.asyncio
async def test_git_log(registry):
    result = await registry.get("Git").execute({"subcommand": "log", "args": "--oneline -3"})
    assert len(result) > 0


@pytest.mark.asyncio
async def test_todolist_workflow(registry):
    todo = registry.get("TodoList")
    result = await todo.execute({"action": "create", "items": ["Task A", "Task B"]})
    assert "2" in result

    listed = await todo.execute({"action": "list"})
    assert "Task A" in listed
    assert "Task B" in listed

    await todo.execute({"action": "check", "index": 0})
    listed2 = await todo.execute({"action": "list"})
    assert "[x]" in listed2.lower()

    await todo.execute({"action": "uncheck", "index": 0})
    listed3 = await todo.execute({"action": "list"})
    assert "[ ]" in listed3

    await todo.execute({"action": "clear"})
    listed4 = await todo.execute({"action": "list"})
    assert "no tasks" in listed4.lower()


@pytest.mark.asyncio
async def test_todolist_create_empty(registry):
    todo = registry.get("TodoList")
    result = await todo.execute({"action": "create", "items": []})
    assert "error" in result.lower()


@pytest.mark.asyncio
async def test_todolist_check_out_of_range(registry):
    todo = registry.get("TodoList")
    await todo.execute({"action": "clear"})
    await todo.execute({"action": "create", "items": ["Only item"]})
    result = await todo.execute({"action": "check", "index": 99})
    assert "error" in result.lower() or "out of range" in result.lower()
    await todo.execute({"action": "clear"})


@pytest.mark.asyncio
async def test_todolist_unknown_action(registry):
    todo = registry.get("TodoList")
    result = await todo.execute({"action": "foobar"})
    assert "error" in result.lower() or "unknown" in result.lower()


@pytest.mark.asyncio
async def test_screenshot_placeholder(registry):
    result = await registry.get("Screenshot").execute({})
    assert "screenshot" in result.lower() or "not available" in result.lower()


@pytest.mark.asyncio
async def test_mcp_placeholder(registry):
    result = await registry.get("MCP").execute({})
    assert "mcp" in result.lower() or "not" in result.lower()


@pytest.mark.asyncio
async def test_ask_user(registry):
    result = await registry.get("AskUser").execute({"question": "test?"})
    assert "__ASK_USER__" in result or "ask" in result.lower()


@pytest.mark.asyncio
async def test_ask_user_with_options(registry):
    result = await registry.get("AskUser").execute({
        "question": "pick one",
        "options": ["a", "b", "c"],
    })
    assert "options" in result.lower() or "__ASK_USER__" in result


# ============================================================
# Tool attribute validation
# ============================================================

def test_all_tools_have_name(registry):
    for name, tool in registry._tools.items():
        assert hasattr(tool, "name"), f"{name} missing name"
        assert isinstance(tool.name, str), f"{name}.name is not str"


def test_all_tools_have_description(registry):
    for name, tool in registry._tools.items():
        assert hasattr(tool, "description"), f"{name} missing description"
        assert len(tool.description) > 5, f"{name} description too short"


def test_all_tools_have_parameters(registry):
    for name, tool in registry._tools.items():
        assert hasattr(tool, "parameters"), f"{name} missing parameters"
        assert isinstance(tool.parameters, dict), f"{name} parameters not dict"
        assert "properties" in tool.parameters, f"{name} parameters missing properties"


def test_all_tools_have_execute(registry):
    for name, tool in registry._tools.items():
        assert hasattr(tool, "execute"), f"{name} missing execute method"
        assert callable(tool.execute), f"{name}.execute is not callable"


def test_all_tools_parameters_have_required(registry):
    for name, tool in registry._tools.items():
        assert "required" in tool.parameters, f"{name} parameters missing 'required'"


def test_registry_checkpoint_is_checkpoint_manager(registry):
    assert isinstance(registry.checkpoint, CheckpointManager)
