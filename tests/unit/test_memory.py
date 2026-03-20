"""Tests for memory and context management modules."""
from __future__ import annotations

import pytest

from pikaclaw.memory.project_memory import ProjectMemory
from pikaclaw.memory.embedding_search import EmbeddingSearch
from pikaclaw.memory.sessions import SessionManager
from pikaclaw.context.manager import ContextManager
from pikaclaw.context.compactor import ContextCompactor


# ═══════════════════════════════════════════════════════════
# PROJECT MEMORY
# ═══════════════════════════════════════════════════════════

class TestProjectMemory:
    @pytest.fixture
    def pm(self, tmp_path):
        memory = ProjectMemory()
        memory.db_path = tmp_path / "project.db"
        return memory

    async def test_remember_and_recall(self, pm):
        await pm.remember("favorite_color", "blue", "preferences")
        results = await pm.recall("favorite")
        assert len(results) >= 1
        assert any(r["value"] == "blue" for r in results)

    async def test_recall_by_value(self, pm):
        await pm.remember("animal", "golden retriever", "pets")
        results = await pm.recall("retriever")
        assert len(results) >= 1

    async def test_recall_by_category(self, pm):
        await pm.remember("lang", "python", "tech")
        await pm.remember("editor", "vim", "tech")
        await pm.remember("color", "blue", "prefs")
        results = await pm.recall("", category="tech")
        assert len(results) >= 2

    async def test_forget(self, pm):
        await pm.remember("temp_key", "temp_value")
        removed = await pm.forget("temp_key")
        assert removed
        results = await pm.recall("temp_key")
        assert len(results) == 0

    async def test_forget_nonexistent(self, pm):
        removed = await pm.forget("nonexistent_key")
        assert not removed

    async def test_get_all(self, pm):
        await pm.remember("a", "1", "cat1")
        await pm.remember("b", "2", "cat2")
        all_items = await pm.get_all()
        assert len(all_items) == 2

    async def test_get_all_by_category(self, pm):
        await pm.remember("a", "1", "cat1")
        await pm.remember("b", "2", "cat2")
        items = await pm.get_all(category="cat1")
        assert len(items) == 1

    async def test_remember_updates_existing(self, pm):
        await pm.remember("key", "old_value")
        await pm.remember("key", "new_value")
        results = await pm.recall("key")
        assert len(results) == 1
        assert results[0]["value"] == "new_value"


# ═══════════════════════════════════════════════════════════
# EMBEDDING SEARCH
# ═══════════════════════════════════════════════════════════

class TestEmbeddingSearch:
    def test_add_and_search(self):
        es = EmbeddingSearch()
        es.add("Python is a programming language")
        es.add("JavaScript runs in the browser")
        es.add("Rust is a systems programming language")
        results = es.search("programming language")
        assert len(results) >= 2

    def test_search_no_results(self):
        es = EmbeddingSearch()
        es.add("hello world")
        results = es.search("quantum physics")
        assert len(results) == 0

    def test_cosine_similarity_identical(self):
        sim = EmbeddingSearch.cosine_similarity([1.0, 0.0, 1.0], [1.0, 0.0, 1.0])
        assert sim == pytest.approx(1.0)

    def test_cosine_similarity_orthogonal(self):
        sim = EmbeddingSearch.cosine_similarity([1.0, 0.0], [0.0, 1.0])
        assert sim == pytest.approx(0.0)

    def test_cosine_similarity_empty(self):
        assert EmbeddingSearch.cosine_similarity([], [1.0]) == 0.0
        assert EmbeddingSearch.cosine_similarity([], []) == 0.0

    def test_cosine_similarity_different_lengths(self):
        sim = EmbeddingSearch.cosine_similarity([1.0, 1.0], [1.0, 1.0, 0.0])
        assert sim > 0.0

    def test_tfidf_vector(self):
        es = EmbeddingSearch()
        es.add("hello world")
        vec = es._tfidf_vector("hello world")
        assert len(vec) > 0
        assert any(v > 0 for v in vec)


# ═══════════════════════════════════════════════════════════
# SESSION MANAGER
# ═══════════════════════════════════════════════════════════

class TestSessionManager:
    @pytest.fixture
    def sm(self, tmp_path):
        manager = SessionManager()
        manager.db_path = tmp_path / "sessions.db"
        return manager

    async def test_save_and_load(self, sm):
        from dataclasses import dataclass, field

        @dataclass
        class FakeState:
            active_agent: str = "build"
            current_model: str = "test-model"
            messages: list = field(default_factory=lambda: [{"role": "user", "content": "hello"}])
            turn_count: int = 5
            total_input_tokens: int = 100
            total_output_tokens: int = 200

        await sm.save_session("test-session-1", FakeState())
        loaded = await sm.load_session("test-session-1")
        assert loaded is not None
        assert loaded["agent"] == "build"

    async def test_load_nonexistent(self, sm):
        result = await sm.load_session("nonexistent")
        assert result is None

    async def test_list_sessions(self, sm):
        from dataclasses import dataclass, field

        @dataclass
        class FakeState:
            active_agent: str = "build"
            current_model: str = "test"
            messages: list = field(default_factory=list)
            turn_count: int = 0
            total_input_tokens: int = 0
            total_output_tokens: int = 0

        await sm.save_session("s1", FakeState())
        await sm.save_session("s2", FakeState(active_agent="plan"))
        sessions = await sm.list_sessions()
        assert len(sessions) == 2

    async def test_delete_session(self, sm):
        from dataclasses import dataclass, field

        @dataclass
        class FakeState:
            active_agent: str = "build"
            current_model: str = "test"
            messages: list = field(default_factory=list)
            turn_count: int = 0
            total_input_tokens: int = 0
            total_output_tokens: int = 0

        await sm.save_session("to-delete", FakeState())
        deleted = await sm.delete_session("to-delete")
        assert deleted
        assert await sm.load_session("to-delete") is None


# ═══════════════════════════════════════════════════════════
# CONTEXT MANAGER
# ═══════════════════════════════════════════════════════════

class TestContextManager:
    def test_estimate_tokens(self):
        cm = ContextManager()
        tokens = cm.estimate_tokens("hello world " * 100)
        assert tokens > 0
        assert tokens == pytest.approx(len("hello world " * 100) // 4)

    def test_track_message(self):
        cm = ContextManager()
        tokens = cm.track_message({"role": "user", "content": "hello world"})
        assert tokens > 0
        assert cm.usage_percent > 0

    def test_needs_compaction_false(self):
        cm = ContextManager()
        cm.track_message({"role": "user", "content": "short message"})
        assert not cm.needs_compaction()

    def test_needs_compaction_true(self):
        cm = ContextManager()
        cm._token_count = 120000
        assert cm.needs_compaction()

    def test_reset(self):
        cm = ContextManager()
        cm.track_message({"role": "user", "content": "hello"})
        cm.reset()
        assert cm.usage_percent == 0.0


# ═══════════════════════════════════════════════════════════
# CONTEXT COMPACTOR
# ═══════════════════════════════════════════════════════════

class TestContextCompactor:
    def test_compact_short_conversation(self):
        cc = ContextCompactor()
        messages = [{"role": "user", "content": "hi"}]
        result = cc.compact(messages, keep_recent=10)
        assert len(result) == 1

    def test_compact_long_conversation(self):
        cc = ContextCompactor()
        messages = [{"role": "user", "content": f"message {i}"} for i in range(25)]
        result = cc.compact(messages, keep_recent=5)
        # Should have 1 summary + 5 recent = 6
        assert len(result) == 6
        assert "Context Summary" in result[0]["content"]

    def test_compact_preserves_recent(self):
        cc = ContextCompactor()
        messages = [{"role": "user", "content": f"msg {i}"} for i in range(20)]
        result = cc.compact(messages, keep_recent=3)
        assert result[-1]["content"] == "msg 19"
        assert result[-2]["content"] == "msg 18"
        assert result[-3]["content"] == "msg 17"
