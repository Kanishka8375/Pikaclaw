"""FeedbackAnalyzer — aggregates feedback into actionable patterns for Darwin.

This is the bridge between raw user complaints and Darwin's Weakness model.
It reads from FeedbackCollector and produces Weakness objects that the
observatory can merge into its diagnosis.

Pattern detection:
    1. Category frequency: which complaint types appear most?
    2. Agent correlation:   which agents get the most negative feedback?
    3. Model correlation:   which models produce the worst outcomes?
    4. Time clustering:     are problems getting worse or better?
    5. Severity scoring:    combines rating + frequency + recency
"""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timedelta

from pikaclaw.darwin.observatory import Weakness
from pikaclaw.feedback.collector import FeedbackCollector, FeedbackEntry


# Maps feedback categories → Darwin weakness categories + improvement techniques
CATEGORY_TO_WEAKNESS = {
    "wrong_answer":   ("accuracy",       "prompt_refinement"),
    "misunderstood":  ("comprehension",  "intent_parsing"),
    "incomplete":     ("completeness",   "multi_step_planning"),
    "slow":           ("performance",    "model_routing"),
    "tool_failure":   ("tool_reliability", "tool_error_handling"),
    "bad_code":       ("code_quality",   "code_review_loop"),
    "hallucination":  ("hallucination",  "grounding_verification"),
    "repetitive":     ("loop_detection", "conversation_tracking"),
    "unsafe":         ("safety",         "security_hardening"),
    "other":          ("general",        "prompt_refinement"),
}


@dataclass
class FeedbackPattern:
    """An aggregated pattern extracted from multiple feedback entries."""
    weakness_category: str
    technique: str
    severity: float          # 0.0 - 1.0
    count: int
    avg_rating: float
    description: str
    sample_comments: list[str]
    affected_agents: list[str]
    affected_models: list[str]


class FeedbackAnalyzer:
    """Analyzes collected feedback and produces weakness patterns for Darwin."""

    def __init__(self, collector: FeedbackCollector | None = None):
        self.collector = collector or FeedbackCollector()

    async def analyze(self, days: int = 7, min_count: int = 2) -> list[FeedbackPattern]:
        """Analyze recent feedback and extract patterns.

        Args:
            days: Look back window
            min_count: Minimum feedback entries to form a pattern
                       (1 complaint is noise, 2+ is a pattern)
        """
        entries = await self.collector.get_recent(days=days)
        if not entries:
            return []

        # Group by category
        by_category: dict[str, list[FeedbackEntry]] = {}
        for entry in entries:
            by_category.setdefault(entry.category, []).append(entry)

        patterns: list[FeedbackPattern] = []
        for category, group in by_category.items():
            if len(group) < min_count:
                continue

            weakness_cat, technique = CATEGORY_TO_WEAKNESS.get(
                category, ("general", "prompt_refinement")
            )

            # Compute severity from multiple signals
            ratings = [e.rating for e in group if e.rating > 0]
            avg_rating = sum(ratings) / len(ratings) if ratings else 0.0

            # Severity formula:
            # - Low ratings increase severity
            # - More complaints increase severity
            # - Recent complaints weight more (recency bias)
            rating_severity = (5.0 - avg_rating) / 4.0 if avg_rating > 0 else 0.5
            volume_severity = min(1.0, len(group) / 10.0)
            recency_severity = self._recency_weight(group)
            severity = (rating_severity * 0.4) + (volume_severity * 0.3) + (recency_severity * 0.3)
            severity = min(1.0, max(0.0, severity))

            # Collect affected agents and models
            agents = list({e.agent for e in group if e.agent})
            models = list({e.model for e in group if e.model})

            # Collect sample comments (unique, non-empty)
            comments = list({e.comment for e in group if e.comment})[:5]

            description = self._build_description(category, group, avg_rating)

            patterns.append(FeedbackPattern(
                weakness_category=weakness_cat,
                technique=technique,
                severity=severity,
                count=len(group),
                avg_rating=avg_rating,
                description=description,
                sample_comments=comments,
                affected_agents=agents,
                affected_models=models,
            ))

        # Sort by severity (worst first)
        patterns.sort(key=lambda p: p.severity, reverse=True)
        return patterns

    async def to_weaknesses(self, days: int = 7, min_count: int = 2) -> list[Weakness]:
        """Convert feedback patterns into Darwin Weakness objects.

        This is the key method — it translates user pain into
        something Darwin's evolution cycle can act on.
        """
        patterns = await self.analyze(days=days, min_count=min_count)
        weaknesses: list[Weakness] = []

        for pattern in patterns:
            weaknesses.append(Weakness(
                category=pattern.weakness_category,
                severity=pattern.severity,
                description=pattern.description,
                sample_count=pattern.count,
            ))

        return weaknesses

    async def get_agent_report(self, days: int = 7) -> dict[str, dict]:
        """Get per-agent feedback report.

        Returns: { "build": {"count": 5, "avg_rating": 2.3, "top_complaint": "wrong_answer"}, ... }
        """
        entries = await self.collector.get_recent(days=days)
        by_agent: dict[str, list[FeedbackEntry]] = {}
        for e in entries:
            if e.agent:
                by_agent.setdefault(e.agent, []).append(e)

        report: dict[str, dict] = {}
        for agent, group in by_agent.items():
            ratings = [e.rating for e in group if e.rating > 0]
            categories = Counter(e.category for e in group)
            report[agent] = {
                "count": len(group),
                "avg_rating": round(sum(ratings) / len(ratings), 2) if ratings else 0.0,
                "top_complaint": categories.most_common(1)[0][0] if categories else None,
                "categories": dict(categories),
            }
        return report

    async def get_trend(self, days: int = 14) -> list[dict]:
        """Get daily feedback trend (is satisfaction improving or declining?).

        Returns list of daily summaries, newest first.
        """
        entries = await self.collector.get_recent(days=days, limit=500)
        by_day: dict[str, list[FeedbackEntry]] = {}
        for e in entries:
            day = e.timestamp[:10]  # YYYY-MM-DD
            by_day.setdefault(day, []).append(e)

        trend: list[dict] = []
        for day in sorted(by_day.keys(), reverse=True):
            group = by_day[day]
            ratings = [e.rating for e in group if e.rating > 0]
            trend.append({
                "date": day,
                "count": len(group),
                "avg_rating": round(sum(ratings) / len(ratings), 2) if ratings else 0.0,
                "explicit": sum(1 for e in group if e.source == "explicit"),
                "implicit": sum(1 for e in group if e.source == "implicit"),
            })
        return trend

    def _recency_weight(self, entries: list[FeedbackEntry]) -> float:
        """Compute recency weight: recent complaints matter more."""
        if not entries:
            return 0.0
        now = datetime.utcnow()
        weights = []
        for e in entries:
            try:
                ts = datetime.fromisoformat(e.timestamp)
                hours_ago = (now - ts).total_seconds() / 3600
                # Exponential decay: 1.0 for now, 0.5 for 24h ago, 0.25 for 48h
                weight = 0.5 ** (hours_ago / 24)
                weights.append(weight)
            except (ValueError, TypeError):
                weights.append(0.5)
        return sum(weights) / len(weights) if weights else 0.0

    def _build_description(self, category: str, entries: list[FeedbackEntry], avg_rating: float) -> str:
        """Build a human-readable description of a feedback pattern."""
        label = category.replace("_", " ")
        count = len(entries)
        comments_with_text = [e for e in entries if e.comment]

        desc = f"Users reported '{label}' {count} times"
        if avg_rating > 0:
            desc += f" (avg rating: {avg_rating:.1f}/5)"

        # Add the most informative comment
        if comments_with_text:
            best = max(comments_with_text, key=lambda e: len(e.comment))
            desc += f". Example: \"{best.comment[:150]}\""

        return desc
