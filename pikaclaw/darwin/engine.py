"""Darwin Engine — the main orchestrator for self-evolution."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from pikaclaw.darwin.observatory import PerformanceObservatory
from pikaclaw.darwin.lab import ResearchLab, HypothesisGenerator
from pikaclaw.darwin.forge import CodeForge
from pikaclaw.darwin.crucible import TestCrucible
from pikaclaw.darwin.arena import BenchmarkArena
from pikaclaw.darwin.genome import EvolutionGenome
from pikaclaw.darwin.deployment import DeploymentPipeline
from pikaclaw.darwin.chronicle import LearningChronicle
from pikaclaw.darwin.constraints import DarwinConstraints
from pikaclaw.darwin.watchdog import DarwinWatchdog
from pikaclaw.darwin.anti_hallucination import AntiHallucinationPipeline

if TYPE_CHECKING:
    from pikaclaw.config.schema import PikaClawConfig
    from pikaclaw.models.router import ModelRouter
    from pikaclaw.tools.registry import ToolRegistry


@dataclass
class EvolutionResult:
    """Result of a single evolution cycle."""
    weaknesses_found: int = 0
    hypotheses_generated: int = 0
    patches_tested: int = 0
    patches_deployed: int = 0
    improvements: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


@dataclass
class DarwinStatus:
    """Current status of the Darwin engine."""
    generation: int = 0
    total_improvements: int = 0
    pending_hypotheses: int = 0
    last_cycle: str = ""
    enabled: bool = False


class DarwinEngine:
    """Main orchestrator for PikaClaw's self-evolution."""

    def __init__(self, config: PikaClawConfig, model_router: ModelRouter, tool_registry: ToolRegistry):
        self.config = config
        self.router = model_router
        self.tools = tool_registry

        # Initialize all components
        self.observatory = PerformanceObservatory()
        self.lab = ResearchLab()
        self.hypothesis_gen = HypothesisGenerator()
        self.forge = CodeForge(model_router)
        self.crucible = TestCrucible()
        self.arena = BenchmarkArena()
        self.genome = EvolutionGenome()
        self.deployment = DeploymentPipeline()
        self.chronicle = LearningChronicle()
        self.constraints = DarwinConstraints()
        self.watchdog = DarwinWatchdog()
        self.anti_hallucination = AntiHallucinationPipeline(model_router)

        # Feedback integration (lazy-loaded)
        self._feedback_collector = None
        self._feedback_analyzer = None
        self._last_cycle = ""

    @property
    def feedback_collector(self):
        if self._feedback_collector is None:
            try:
                from pikaclaw.feedback.collector import FeedbackCollector
                self._feedback_collector = FeedbackCollector()
            except ImportError:
                pass
        return self._feedback_collector

    @property
    def feedback_analyzer(self):
        if self._feedback_analyzer is None:
            try:
                from pikaclaw.feedback.analyzer import FeedbackAnalyzer
                self._feedback_analyzer = FeedbackAnalyzer()
            except ImportError:
                pass
        return self._feedback_analyzer

    async def evolution_cycle(self) -> EvolutionResult:
        """Run a complete evolution cycle.

        1. Observe: diagnose weaknesses
        2. Research: scan for techniques
        3. Hypothesize: generate improvement ideas
        4. For each hypothesis: validate → implement → test → benchmark → deploy
        5. Record results
        """
        result = EvolutionResult()

        # Verify integrity before starting
        ok, violations = self.watchdog.verify_integrity()
        if not ok:
            result.errors.append(f"Integrity check failed: {violations}")
            return result

        # Step 1: Diagnose weaknesses
        weaknesses = await self.observatory.diagnose()
        result.weaknesses_found = len(weaknesses)

        if not weaknesses:
            result.errors.append("No weaknesses found — system is performing well")
            return result

        # Step 2: Generate hypotheses
        hypotheses = self.hypothesis_gen.generate(weaknesses)
        result.hypotheses_generated = len(hypotheses)

        # Step 3: Process top hypotheses
        for hypothesis in hypotheses[:2]:
            # Validate constraints
            patch = await self.forge.implement(hypothesis)
            constraint_result = self.constraints.validate_patch(patch)
            if not constraint_result.passed:
                result.errors.append(f"Constraint violation for {hypothesis.technique}: {constraint_result.violations}")
                await self.chronicle.record(
                    hypothesis={"technique": hypothesis.technique, "description": hypothesis.description},
                    technique=hypothesis.technique,
                    verdict="rejected",
                    lesson=f"Constraint violations: {constraint_result.violations}",
                )
                continue

            # Test
            verdict = await self.crucible.test(patch)
            result.patches_tested += 1
            if not verdict.passed:
                result.errors.append(f"Test failed for {hypothesis.technique}: {verdict.errors}")
                await self.chronicle.record(
                    hypothesis={"technique": hypothesis.technique, "description": hypothesis.description},
                    technique=hypothesis.technique,
                    verdict="failed",
                    lesson=f"Failed gates: {[g for g, v in verdict.gates.items() if not v]}",
                )
                continue

            # Benchmark
            bench = await self.arena.benchmark(patch, hypothesis)

            # Commit
            commit_hash = await self.genome.commit(patch, hypothesis)

            # Deploy (only if benchmark shows improvement)
            if bench.improved:
                deploy_result = await self.deployment.deploy(patch, patch_id=commit_hash)
                if deploy_result.success:
                    result.patches_deployed += 1
                    result.improvements.append(f"{hypothesis.technique}: +{bench.delta:.1f}")
                    # Close the feedback loop: mark related feedback as resolved
                    await self._resolve_related_feedback(hypothesis, commit_hash)
                else:
                    result.errors.append(f"Deploy failed for {hypothesis.technique}: {deploy_result.errors}")

            # Record in chronicle
            await self.chronicle.record(
                hypothesis={"technique": hypothesis.technique, "description": hypothesis.description},
                technique=hypothesis.technique,
                verdict="pass" if bench.improved else "no_improvement",
                improvement=bench.delta,
                lesson=f"{'Improved' if bench.improved else 'No improvement'}: {bench.details}",
            )

        from datetime import datetime
        self._last_cycle = datetime.utcnow().isoformat()
        return result

    def get_status(self) -> DarwinStatus:
        """Get current Darwin engine status."""
        return DarwinStatus(
            generation=self.genome.get_generation(),
            total_improvements=0,
            pending_hypotheses=0,
            last_cycle=self._last_cycle,
            enabled=self.config.darwin.enabled if self.config else False,
        )

    async def get_metrics(self, days: int = 7):
        """Get performance metrics from the observatory."""
        return await self.observatory.get_metrics(days)

    async def diagnose(self):
        """Diagnose current weaknesses."""
        return await self.observatory.diagnose()

    async def get_log(self, limit: int = 20):
        """Get experiment log from the chronicle."""
        return await self.chronicle.get_history(limit)

    async def get_feedback_summary(self, days: int = 7) -> dict:
        """Get user feedback summary. Surfaces what users are unhappy about."""
        if self.feedback_collector:
            return await self.feedback_collector.get_satisfaction_score(days)
        return {"total_feedback": 0, "avg_rating": 0, "resolution_rate": 0}

    async def _resolve_related_feedback(self, hypothesis, resolution_id: str) -> int:
        """Mark feedback entries as resolved when Darwin deploys a fix.

        Maps hypothesis techniques back to feedback categories and marks
        matching unresolved entries as addressed.
        """
        if not self.feedback_collector:
            return 0

        from pikaclaw.feedback.analyzer import CATEGORY_TO_WEAKNESS

        # Reverse map: technique → feedback categories
        technique_to_categories: dict[str, list[str]] = {}
        for fb_cat, (_, technique) in CATEGORY_TO_WEAKNESS.items():
            technique_to_categories.setdefault(technique, []).append(fb_cat)

        # Find which feedback categories this hypothesis addresses
        target_categories = technique_to_categories.get(hypothesis.technique, [])
        if not target_categories:
            return 0

        resolved_count = 0
        for category in target_categories:
            entries = await self.feedback_collector.get_by_category(category)
            for entry in entries:
                if not entry.resolved:
                    await self.feedback_collector.mark_resolved(entry.id, resolution_id)
                    resolved_count += 1

        return resolved_count
