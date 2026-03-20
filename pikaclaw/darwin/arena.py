"""Benchmark Arena — compares old vs new performance."""
from __future__ import annotations

import time
from dataclasses import dataclass, field

from pikaclaw.darwin.constraints import CodePatch
from pikaclaw.darwin.lab import Hypothesis


@dataclass
class BenchmarkResult:
    """Result of benchmarking a patch."""
    improved: bool = False
    old_score: float = 0.0
    new_score: float = 0.0
    delta: float = 0.0
    details: dict = field(default_factory=dict)

    @property
    def improvement_percent(self) -> float:
        if self.old_score == 0:
            return 0.0
        return ((self.new_score - self.old_score) / self.old_score) * 100


class BenchmarkArena:
    """Benchmarks patches against baseline to verify improvements."""

    def __init__(self):
        self._baselines: dict[str, float] = {}

    def set_baseline(self, metric: str, value: float) -> None:
        """Set a baseline metric value."""
        self._baselines[metric] = value

    async def benchmark(self, patch: CodePatch, hypothesis: Hypothesis) -> BenchmarkResult:
        """Compare patch performance against baseline.

        For now, uses heuristic scoring based on patch quality.
        In production, would run actual test tasks with both versions.
        """
        details: dict = {}

        # Score based on patch characteristics
        old_score = self._baselines.get(hypothesis.technique, 50.0)

        # Heuristic new score based on patch quality
        new_score = old_score
        bonuses = 0.0

        # Bonus for having tests
        if patch.tests:
            bonuses += 5.0
            details["has_tests"] = True

        # Bonus for reasonable size
        lines = patch.total_lines
        if 10 <= lines <= 200:
            bonuses += 3.0
            details["reasonable_size"] = True
        elif lines > 500:
            bonuses -= 5.0
            details["too_large"] = True

        # Bonus for docstrings
        has_docs = any('"""' in content or "'''" in content for content in patch.files.values())
        if has_docs:
            bonuses += 2.0
            details["has_docs"] = True

        # Bonus for type hints
        has_types = any(": " in content and " ->" in content for content in patch.files.values())
        if has_types:
            bonuses += 2.0
            details["has_types"] = True

        new_score = old_score + bonuses
        delta = new_score - old_score
        improved = delta > 0

        return BenchmarkResult(
            improved=improved,
            old_score=old_score,
            new_score=new_score,
            delta=delta,
            details=details,
        )
