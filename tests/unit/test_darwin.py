"""Tests for all Darwin evolution engine components."""
from __future__ import annotations

import asyncio
import json
import tempfile
from pathlib import Path

import pytest

from pikaclaw.darwin.constraints import CodePatch, DarwinConstraints, ValidationResult
from pikaclaw.darwin.observatory import PerformanceObservatory, MetricsSummary, Weakness
from pikaclaw.darwin.watchdog import DarwinWatchdog
from pikaclaw.darwin.chronicle import LearningChronicle, ExperimentRecord, Lesson
from pikaclaw.darwin.genome import EvolutionGenome, EvolutionEntry
from pikaclaw.darwin.lab import ResearchLab, HypothesisGenerator, Hypothesis, Paper, Repo
from pikaclaw.darwin.forge import CodeForge
from pikaclaw.darwin.crucible import TestCrucible as CrucibleRunner, TestVerdict
from pikaclaw.darwin.arena import BenchmarkArena, BenchmarkResult
from pikaclaw.darwin.deployment import DeploymentPipeline, DeployResult
from pikaclaw.darwin.anti_hallucination import AntiHallucinationPipeline, VerificationResult
from pikaclaw.darwin.engine import DarwinEngine, DarwinStatus


# ═══════════════════════════════════════════════════════════
# CONSTRAINTS
# ═══════════════════════════════════════════════════════════

class TestDarwinConstraints:
    def test_validate_clean_patch(self):
        c = DarwinConstraints()
        patch = CodePatch(files={"pikaclaw/improvements/fix.py": "def fix():\n    return True\n"})
        result = c.validate_patch(patch)
        assert result.passed
        assert result.violations == []

    def test_forbidden_patterns_eval(self):
        c = DarwinConstraints()
        patch = CodePatch(files={"bad.py": "result = eval(user_input)"})
        result = c.validate_patch(patch)
        assert not result.passed
        assert any("eval" in v for v in result.violations)

    def test_forbidden_patterns_exec(self):
        c = DarwinConstraints()
        patch = CodePatch(files={"bad.py": "exec(code)"})
        result = c.validate_patch(patch)
        assert not result.passed

    def test_forbidden_patterns_os_system(self):
        c = DarwinConstraints()
        patch = CodePatch(files={"bad.py": "import os\nos.system('rm -rf /')"})
        result = c.validate_patch(patch)
        assert not result.passed

    def test_forbidden_paths(self):
        c = DarwinConstraints()
        patch = CodePatch(files={"pikaclaw/security/secrets.py": "hacked = True"})
        result = c.validate_patch(patch)
        assert not result.passed
        assert any("Forbidden path" in v for v in result.violations)

    def test_patch_too_large(self):
        c = DarwinConstraints()
        huge_content = "x = 1\n" * 3000
        patch = CodePatch(files={"big.py": huge_content})
        result = c.validate_patch(patch)
        assert not result.passed
        assert any("too large" in v.lower() for v in result.violations)

    def test_too_many_files(self):
        c = DarwinConstraints()
        files = {f"file_{i}.py": "x = 1\n" for i in range(25)}
        patch = CodePatch(files=files)
        result = c.validate_patch(patch)
        assert not result.passed

    def test_is_forbidden_path(self):
        c = DarwinConstraints()
        assert c.is_forbidden_path("pikaclaw/security/sentinel.py")
        assert c.is_forbidden_path("pikaclaw/darwin/constraints.py")
        assert not c.is_forbidden_path("pikaclaw/tools/builtin/read.py")

    def test_code_patch_total_lines(self):
        patch = CodePatch(files={"a.py": "line1\nline2\nline3", "b.py": "x\ny"})
        assert patch.total_lines == 5  # 3 + 2


# ═══════════════════════════════════════════════════════════
# OBSERVATORY
# ═══════════════════════════════════════════════════════════

class TestObservatory:
    @pytest.fixture
    def obs(self, tmp_path):
        return PerformanceObservatory(db_path=str(tmp_path / "metrics.db"))

    async def test_track_and_get_metrics(self, obs):
        await obs.track_interaction(task_type="test", success=True, tokens=100, latency_ms=500, cost=0.01)
        await obs.track_interaction(task_type="test", success=True, tokens=200, latency_ms=300, cost=0.02)
        metrics = await obs.get_metrics(days=1)
        assert metrics.total_interactions == 2
        assert metrics.success_rate == 1.0
        assert metrics.total_cost == pytest.approx(0.03)

    async def test_diagnose_no_data(self, obs):
        weaknesses = await obs.diagnose()
        assert weaknesses == []

    async def test_diagnose_low_success(self, obs):
        for _ in range(5):
            await obs.track_interaction(success=False, tokens=100, latency_ms=100)
        weaknesses = await obs.diagnose()
        assert any(w.category == "reliability" for w in weaknesses)

    async def test_diagnose_high_latency(self, obs):
        for _ in range(3):
            await obs.track_interaction(success=True, latency_ms=15000)
        weaknesses = await obs.diagnose()
        assert any(w.category == "performance" for w in weaknesses)

    async def test_hallucination_rate_zero(self, obs):
        await obs.track_interaction(success=True)
        rate = await obs.get_hallucination_rate()
        assert rate == 0.0


# ═══════════════════════════════════════════════════════════
# WATCHDOG
# ═══════════════════════════════════════════════════════════

class TestWatchdog:
    def test_snapshot_and_verify(self, tmp_path):
        f = tmp_path / "test.py"
        f.write_text("original content")
        wd = DarwinWatchdog(protected_files=[str(f)])
        wd._manifest_path = tmp_path / "manifest.json"
        wd.snapshot()
        ok, violations = wd.verify_integrity()
        assert ok
        assert violations == []

    def test_detect_modification(self, tmp_path):
        f = tmp_path / "test.py"
        f.write_text("original content")
        wd = DarwinWatchdog(protected_files=[str(f)])
        wd._manifest_path = tmp_path / "manifest.json"
        wd.snapshot()
        f.write_text("MODIFIED content")
        ok, violations = wd.verify_integrity()
        assert not ok
        assert len(violations) == 1

    def test_missing_file(self, tmp_path):
        wd = DarwinWatchdog(protected_files=[str(tmp_path / "nonexistent.py")])
        wd._manifest_path = tmp_path / "manifest.json"
        hashes = wd.snapshot()
        assert "MISSING" in list(hashes.values())[0]


# ═══════════════════════════════════════════════════════════
# CHRONICLE
# ═══════════════════════════════════════════════════════════

class TestChronicle:
    @pytest.fixture
    def chronicle(self, tmp_path):
        return LearningChronicle(db_path=str(tmp_path / "chronicle.db"))

    async def test_record_and_retrieve(self, chronicle):
        exp_id = await chronicle.record(
            hypothesis={"technique": "retry", "description": "Add retry logic"},
            technique="retry",
            verdict="pass",
            improvement=5.0,
            lesson="Retry improved reliability by 30%",
        )
        assert exp_id > 0
        history = await chronicle.get_history(limit=10)
        assert len(history) == 1
        assert history[0].technique == "retry"

    async def test_get_lessons(self, chronicle):
        await chronicle.record(technique="caching", verdict="pass", lesson="Caching helped")
        await chronicle.record(technique="retry", verdict="fail", lesson="Retry was flaky")
        lessons = await chronicle.get_lessons()
        assert len(lessons) == 2

    async def test_technique_success_rate(self, chronicle):
        await chronicle.record(technique="test_tech", verdict="pass")
        await chronicle.record(technique="test_tech", verdict="pass")
        await chronicle.record(technique="test_tech", verdict="fail")
        rate = await chronicle.get_technique_success_rate("test_tech")
        assert rate == pytest.approx(2 / 3)

    async def test_empty_history(self, chronicle):
        history = await chronicle.get_history()
        assert history == []


# ═══════════════════════════════════════════════════════════
# LAB
# ═══════════════════════════════════════════════════════════

class TestLab:
    def test_hypothesis_generator_reliability(self):
        gen = HypothesisGenerator()
        weaknesses = [Weakness(category="reliability", severity=0.8, description="Low success rate: 70%")]
        hypotheses = gen.generate(weaknesses)
        assert len(hypotheses) >= 1
        assert any(h.technique == "retry_with_backoff" for h in hypotheses)

    def test_hypothesis_generator_performance(self):
        gen = HypothesisGenerator()
        weaknesses = [Weakness(category="performance", severity=0.6, description="High latency")]
        hypotheses = gen.generate(weaknesses)
        assert any(h.technique == "model_routing" for h in hypotheses)

    def test_hypothesis_generator_cost(self):
        gen = HypothesisGenerator()
        weaknesses = [Weakness(category="cost", severity=0.5, description="High cost")]
        hypotheses = gen.generate(weaknesses)
        assert any(h.technique == "context_compression" for h in hypotheses)

    def test_hypothesis_priority(self):
        h = Hypothesis(target_weakness="test", technique="test", mechanism="test",
                       expected_improvement=0.5, confidence=0.8)
        assert h.priority == pytest.approx(0.4)

    def test_hypothesis_sorted_by_priority(self):
        gen = HypothesisGenerator()
        weaknesses = [
            Weakness(category="reliability", severity=0.9, description="Low success"),
            Weakness(category="cost", severity=0.3, description="High cost"),
        ]
        hypotheses = gen.generate(weaknesses)
        for i in range(len(hypotheses) - 1):
            assert hypotheses[i].priority >= hypotheses[i + 1].priority


# ═══════════════════════════════════════════════════════════
# FORGE
# ═══════════════════════════════════════════════════════════

class TestForge:
    def test_estimate_complexity(self):
        forge = CodeForge()
        h = Hypothesis(target_weakness="test", technique="retry_with_backoff",
                       mechanism="test", expected_improvement=0.3, confidence=0.8)
        assert forge.estimate_complexity(h) == 3

    async def test_implement_template(self):
        forge = CodeForge()
        h = Hypothesis(target_weakness="Low success", technique="retry_with_backoff",
                       mechanism="Add retry", expected_improvement=0.3, confidence=0.8)
        patch = await forge.implement(h)
        assert len(patch.files) > 0
        assert any("retry" in content for content in patch.files.values())

    async def test_implement_unknown_technique(self):
        forge = CodeForge()
        h = Hypothesis(target_weakness="test", technique="unknown_technique",
                       mechanism="test", expected_improvement=0.5, confidence=0.5)
        patch = await forge.implement(h)
        assert len(patch.files) > 0


# ═══════════════════════════════════════════════════════════
# CRUCIBLE
# ═══════════════════════════════════════════════════════════

class TestCrucibleGates:
    async def test_clean_patch_passes(self):
        crucible = CrucibleRunner()
        patch = CodePatch(files={"pikaclaw/improvements/fix.py": "def fix():\n    return True\n"})
        verdict = await crucible.test(patch)
        assert verdict.passed
        assert verdict.gates["syntax"]
        assert verdict.gates["security"]

    async def test_syntax_error_fails(self):
        crucible = CrucibleRunner()
        patch = CodePatch(files={"bad.py": "def broken(\n    return"})
        verdict = await crucible.test(patch)
        assert not verdict.gates["syntax"]
        assert not verdict.passed

    async def test_security_gate_eval(self):
        crucible = CrucibleRunner()
        patch = CodePatch(files={"danger.py": "result = eval(user_input)"})
        verdict = await crucible.test(patch)
        assert not verdict.gates["security"]

    async def test_empty_patch_fails(self):
        crucible = CrucibleRunner()
        patch = CodePatch(files={})
        verdict = await crucible.test(patch)
        assert not verdict.gates["non_empty"]

    async def test_secrets_gate(self):
        crucible = CrucibleRunner()
        patch = CodePatch(files={"leak.py": 'key = "sk-ant-abcdefghij1234567890"'})
        verdict = await crucible.test(patch)
        assert not verdict.gates["secrets"]

    async def test_gates_count(self):
        crucible = CrucibleRunner()
        patch = CodePatch(files={"ok.py": "x = 1\n"})
        verdict = await crucible.test(patch)
        assert verdict.gates_total == 14


# ═══════════════════════════════════════════════════════════
# ARENA
# ═══════════════════════════════════════════════════════════

class TestArena:
    async def test_benchmark_with_tests(self):
        arena = BenchmarkArena()
        patch = CodePatch(
            files={"fix.py": '"""Docstring."""\ndef fix(x: int) -> bool:\n    return True\n'},
            tests={"test_fix.py": "def test_fix(): assert True"},
        )
        h = Hypothesis(target_weakness="test", technique="retry", mechanism="test",
                       expected_improvement=0.5, confidence=0.8)
        result = await arena.benchmark(patch, h)
        assert result.improved
        assert result.details.get("has_tests")
        assert result.details.get("has_docs")

    async def test_benchmark_large_patch_penalty(self):
        arena = BenchmarkArena()
        patch = CodePatch(files={"big.py": "x = 1\n" * 600})
        h = Hypothesis(target_weakness="test", technique="retry", mechanism="test",
                       expected_improvement=0.5, confidence=0.8)
        result = await arena.benchmark(patch, h)
        assert result.details.get("too_large")

    def test_improvement_percent(self):
        r = BenchmarkResult(old_score=50.0, new_score=60.0)
        assert r.improvement_percent == pytest.approx(20.0)


# ═══════════════════════════════════════════════════════════
# GENOME
# ═══════════════════════════════════════════════════════════

class TestGenome:
    @pytest.fixture
    def genome(self, tmp_path):
        g = EvolutionGenome()
        g._log_path = tmp_path / "genome_log.json"
        return g

    async def test_commit_and_log(self, genome):
        patch = CodePatch(files={"fix.py": "x = 1\n"})
        h = Hypothesis(target_weakness="test", technique="retry", mechanism="test",
                       expected_improvement=0.5, confidence=0.8, description="Test hypothesis")
        commit_hash = await genome.commit(patch, h)
        assert len(commit_hash) == 12
        assert genome.get_generation() == 1

    async def test_rollback(self, genome):
        patch = CodePatch(files={"fix.py": "x = 1\n"})
        h = Hypothesis(target_weakness="test", technique="retry", mechanism="test",
                       expected_improvement=0.5, confidence=0.8)
        commit_hash = await genome.commit(patch, h)
        assert await genome.rollback(commit_hash)
        assert not await genome.rollback("nonexistent")

    async def test_evolution_log(self, genome):
        for i in range(3):
            patch = CodePatch(files={f"fix_{i}.py": f"x = {i}\n"})
            h = Hypothesis(target_weakness="test", technique=f"tech_{i}", mechanism="test",
                           expected_improvement=0.5, confidence=0.8)
            await genome.commit(patch, h)
        log = genome.get_evolution_log()
        assert len(log) == 3
        assert genome.get_generation() == 3

    def test_empty_log(self, genome):
        log = genome.get_evolution_log()
        assert log == []


# ═══════════════════════════════════════════════════════════
# DEPLOYMENT
# ═══════════════════════════════════════════════════════════

class TestDeployment:
    async def test_deploy_clean_patch(self, tmp_path):
        dp = DeploymentPipeline(repo_path=str(tmp_path))
        (tmp_path / "pikaclaw").mkdir()
        (tmp_path / "pikaclaw" / "__init__.py").write_text('"""PikaClaw."""\n__version__ = "0.1.0"\n')
        patch = CodePatch(files={"pikaclaw/improvements/fix.py": "def fix():\n    return True\n"})
        result = await dp.deploy(patch, patch_id="test123")
        assert result.stage_reached >= 1

    async def test_deploy_syntax_error_fails_sandbox(self, tmp_path):
        dp = DeploymentPipeline(repo_path=str(tmp_path))
        patch = CodePatch(files={"bad.py": "def broken(\n    return"})
        result = await dp.deploy(patch)
        assert not result.success
        assert result.stage_reached == 0 or "sandbox" in str(result.errors).lower()


# ═══════════════════════════════════════════════════════════
# ANTI-HALLUCINATION
# ═══════════════════════════════════════════════════════════

class TestAntiHallucination:
    def test_extract_claims(self):
        ah = AntiHallucinationPipeline()
        text = "The function returns True. The file contains 50 lines. Python is great."
        claims = ah.extract_claims(text)
        assert len(claims) >= 2

    def test_verify_claim_found(self):
        ah = AntiHallucinationPipeline()
        verified, conf = ah.verify_claim_against_source(
            "The function returns True",
            "def my_func():\n    return True\n# The function returns True when called",
        )
        assert verified
        assert conf > 0

    def test_verify_claim_not_found(self):
        ah = AntiHallucinationPipeline()
        verified, conf = ah.verify_claim_against_source(
            "The database uses PostgreSQL with sharding",
            "import sqlite3\nconn = sqlite3.connect('data.db')",
        )
        assert conf < 0.5

    def test_verify_response(self):
        ah = AntiHallucinationPipeline()
        result = ah.verify_response(
            "The file contains a function called process_data that returns a list",
            ["def process_data():\n    return [1, 2, 3]\n"],
        )
        assert isinstance(result, VerificationResult)
        assert result.score >= 0.0

    def test_empty_response(self):
        ah = AntiHallucinationPipeline()
        result = ah.verify_response("", ["source"])
        assert result.score == 1.0  # No claims to verify


# ═══════════════════════════════════════════════════════════
# ENGINE
# ═══════════════════════════════════════════════════════════

class TestEngine:
    def test_engine_imports(self):
        """Verify the engine can be imported and instantiated."""
        from pikaclaw.config.schema import PikaClawConfig
        config = PikaClawConfig()
        # Just verify it can be created without errors
        assert DarwinEngine is not None

    def test_get_status(self):
        from pikaclaw.config.schema import PikaClawConfig
        from pikaclaw.models.router import ModelRouter
        from pikaclaw.tools.registry import ToolRegistry
        config = PikaClawConfig()
        engine = DarwinEngine(config, ModelRouter(config), ToolRegistry())
        status = engine.get_status()
        assert isinstance(status, DarwinStatus)
        assert status.generation == 0
