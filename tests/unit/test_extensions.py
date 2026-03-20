"""Tests for skills, hooks, and daemon extension modules."""
from __future__ import annotations

import pytest

from pikaclaw.skills.loader import SkillLoader
from pikaclaw.hooks.system import HookSystem
from pikaclaw.daemon.service import DaemonService


# ═══════════════════════════════════════════════════════════
# SKILL LOADER
# ═══════════════════════════════════════════════════════════

class TestSkillLoader:
    def test_load_empty_dir(self, tmp_path):
        sl = SkillLoader(skills_dir=str(tmp_path))
        skills = sl.load_all()
        assert skills == {}

    def test_load_skill_file(self, tmp_path):
        skill_file = tmp_path / "debugging.md"
        skill_file.write_text(
            "---\n"
            "name: debugging\n"
            "description: Systematic debugging workflow\n"
            "auto_load: false\n"
            "---\n"
            "Follow this debugging workflow: REPRODUCE → ISOLATE → FIX → VERIFY\n"
        )
        sl = SkillLoader(skills_dir=str(tmp_path))
        skills = sl.load_all()
        assert "debugging" in skills
        assert "REPRODUCE" in skills["debugging"]["content"]

    def test_get_skill(self, tmp_path):
        skill_file = tmp_path / "test.md"
        skill_file.write_text("---\nname: test\n---\nTest content here\n")
        sl = SkillLoader(skills_dir=str(tmp_path))
        sl.load_all()
        assert sl.get_skill("test") is not None
        assert sl.get_skill("nonexistent") is None

    def test_load_nonexistent_dir(self):
        sl = SkillLoader(skills_dir="/tmp/nonexistent_skills_dir_12345")
        skills = sl.load_all()
        assert skills == {}

    def test_load_multiple_skills(self, tmp_path):
        for name in ["skill_a", "skill_b", "skill_c"]:
            (tmp_path / f"{name}.md").write_text(f"---\nname: {name}\n---\nContent of {name}\n")
        sl = SkillLoader(skills_dir=str(tmp_path))
        skills = sl.load_all()
        assert len(skills) == 3


# ═══════════════════════════════════════════════════════════
# HOOK SYSTEM
# ═══════════════════════════════════════════════════════════

class TestHookSystem:
    async def test_register_and_run_pre_hook(self):
        hs = HookSystem()
        hs.register_pre_hook(lambda tool, inp: {**inp, "injected": True})
        result = await hs.run_pre_hooks("Bash", {"command": "echo hi"})
        assert result is not None
        assert result["injected"] is True

    async def test_pre_hook_block(self):
        hs = HookSystem()
        hs.register_pre_hook(lambda tool, inp: None)  # blocks
        result = await hs.run_pre_hooks("Bash", {"command": "rm -rf /"})
        assert result is None

    async def test_post_hook_modifies_output(self):
        hs = HookSystem()
        hs.register_post_hook(lambda tool, inp, out: out + " [modified]")
        result = await hs.run_post_hooks("Read", {}, "file content")
        assert result == "file content [modified]"

    async def test_no_hooks(self):
        hs = HookSystem()
        result = await hs.run_pre_hooks("Bash", {"command": "echo hi"})
        assert result == {"command": "echo hi"}

    async def test_multiple_pre_hooks(self):
        hs = HookSystem()
        hs.register_pre_hook(lambda tool, inp: {**inp, "hook1": True})
        hs.register_pre_hook(lambda tool, inp: {**inp, "hook2": True})
        result = await hs.run_pre_hooks("Bash", {"command": "echo"})
        assert result["hook1"]
        assert result["hook2"]


# ═══════════════════════════════════════════════════════════
# DAEMON SERVICE
# ═══════════════════════════════════════════════════════════

class TestDaemonService:
    async def test_start_stop(self):
        ds = DaemonService()
        assert not ds.is_running
        await ds.start()
        assert ds.is_running
        await ds.stop()
        assert not ds.is_running

    def test_initial_state(self):
        ds = DaemonService()
        assert not ds.is_running
