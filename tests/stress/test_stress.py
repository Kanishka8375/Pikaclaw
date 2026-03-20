"""Stress and edge case tests."""
import pytest
import asyncio
import os
from pikaclaw.tools.registry import ToolRegistry
from pikaclaw.core.messages import TextMessage, ToolCallMessage, DoneMessage
from pikaclaw.config.loader import load_config
from pikaclaw.security.secrets import SecretSanitizer


@pytest.fixture
def registry():
    return ToolRegistry()


@pytest.mark.asyncio
async def test_empty_message(registry):
    """Bash with empty command."""
    result = await registry.get("Bash").execute({"command": ""})
    assert isinstance(result, str)


@pytest.mark.asyncio
async def test_unicode_in_write(registry):
    """Write file with unicode content."""
    path = "/tmp/pk_unicode.txt"
    content = "Hello 世界 🌍 Привет мир"
    await registry.get("Write").execute({"file_path": path, "content": content})
    assert open(path).read() == content
    os.unlink(path)


@pytest.mark.asyncio
async def test_large_output(registry):
    """Bash command with large output."""
    result = await registry.get("Bash").execute({"command": "seq 1 10000"})
    assert "10000" in result


@pytest.mark.asyncio
async def test_binary_file_read(registry):
    """Reading a binary file doesn't crash."""
    path = "/tmp/pk_binary.bin"
    with open(path, "wb") as f:
        f.write(bytes(range(256)))
    result = await registry.get("Read").execute({"file_path": path})
    assert isinstance(result, str)
    os.unlink(path)


@pytest.mark.asyncio
async def test_concurrent_tool_calls(registry):
    """Multiple tools can run concurrently."""
    tasks = [
        registry.get("Bash").execute({"command": "echo 1"}),
        registry.get("Bash").execute({"command": "echo 2"}),
        registry.get("Bash").execute({"command": "echo 3"}),
    ]
    results = await asyncio.gather(*tasks)
    assert len(results) == 3
    assert all("echo" in r or "1" in r or "2" in r or "3" in r for r in results)


@pytest.mark.asyncio
async def test_rapid_undo_redo(registry):
    """Rapid undo/redo doesn't crash."""
    for _ in range(5):
        await registry.get("Undo").execute({})
        await registry.get("Redo").execute({})


@pytest.mark.asyncio
async def test_glob_empty_pattern(registry):
    """Glob with pattern that matches nothing."""
    result = await registry.get("Glob").execute({"pattern": "nonexistent_dir_xyz/**/*.xyz"})
    assert isinstance(result, str)


@pytest.mark.asyncio
async def test_grep_no_matches(registry):
    """Grep with pattern that matches nothing."""
    result = await registry.get("Grep").execute({"pattern": "ZZZNOTFOUNDXYZ", "path": "pikaclaw/"})
    assert isinstance(result, str)


@pytest.mark.asyncio
async def test_edit_empty_file(registry):
    """Edit on empty file."""
    path = "/tmp/pk_empty.txt"
    with open(path, "w") as f:
        pass
    result = await registry.get("Edit").execute({"file_path": path, "old_text": "x", "new_text": "y"})
    assert isinstance(result, str)
    os.unlink(path)


@pytest.mark.asyncio
async def test_todolist_operations(registry):
    """Complex TodoList operations."""
    todo = registry.get("TodoList")
    await todo.execute({"action": "clear"})
    await todo.execute({"action": "create", "items": ["A", "B", "C", "D", "E"]})
    await todo.execute({"action": "check", "index": 0})
    await todo.execute({"action": "check", "index": 2})
    await todo.execute({"action": "check", "index": 4})
    result = await todo.execute({"action": "list"})
    assert "A" in result
    assert "C" in result
    await todo.execute({"action": "clear"})


def test_sanitizer_performance():
    """Sanitizer handles large text quickly."""
    s = SecretSanitizer()
    large_text = "normal text " * 10000
    import time
    start = time.time()
    result = s.sanitize(large_text)
    elapsed = time.time() - start
    assert elapsed < 1.0  # Should be fast


def test_config_load_performance():
    """Config loading is fast."""
    import time
    start = time.time()
    for _ in range(10):
        load_config()
    elapsed = time.time() - start
    assert elapsed < 5.0


def test_message_creation_performance():
    """Creating many messages is fast."""
    import time
    start = time.time()
    for i in range(1000):
        TextMessage(text=f"Message {i}", model="test")
    elapsed = time.time() - start
    assert elapsed < 1.0


@pytest.mark.asyncio
async def test_write_read_roundtrip(registry):
    """Write then read should match."""
    path = "/tmp/pk_roundtrip.txt"
    content = "line 1\nline 2\nline 3"
    await registry.get("Write").execute({"file_path": path, "content": content})
    result = await registry.get("Read").execute({"file_path": path})
    assert "line 1" in result
    assert "line 2" in result
    assert "line 3" in result
    os.unlink(path)


@pytest.mark.asyncio
async def test_special_chars_in_bash(registry):
    """Special characters in bash don't crash."""
    result = await registry.get("Bash").execute({"command": "echo 'hello \"world\" $PATH'"})
    assert isinstance(result, str)


@pytest.mark.asyncio
async def test_git_invalid_subcommand(registry):
    """Invalid git subcommand returns error."""
    result = await registry.get("Git").execute({"subcommand": "not_a_command"})
    assert isinstance(result, str)


@pytest.mark.asyncio
async def test_read_directory_fails_gracefully(registry):
    """Reading a directory returns error, doesn't crash."""
    result = await registry.get("Read").execute({"file_path": "/tmp"})
    assert isinstance(result, str)
