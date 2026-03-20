"""Performance Observatory — tracks metrics and diagnoses weaknesses."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path


@dataclass
class Weakness:
    """An identified weakness in the system."""
    category: str
    severity: float  # 0.0 - 1.0
    description: str
    sample_count: int = 0


@dataclass
class MetricsSummary:
    """Summary of performance metrics."""
    total_interactions: int = 0
    success_rate: float = 0.0
    avg_latency_ms: float = 0.0
    total_cost: float = 0.0
    total_tokens: int = 0
    hallucination_rate: float = 0.0


class PerformanceObservatory:
    """Tracks system performance and diagnoses weaknesses."""

    def __init__(self, db_path: str | None = None):
        self.db_path = Path(db_path) if db_path else Path.home() / ".pikaclaw" / "darwin" / "metrics.db"
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialized = False

    async def _ensure_db(self):
        if self._initialized:
            return
        import aiosqlite
        async with aiosqlite.connect(str(self.db_path)) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS interactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    task_type TEXT DEFAULT 'general',
                    success INTEGER DEFAULT 1,
                    tokens INTEGER DEFAULT 0,
                    latency_ms INTEGER DEFAULT 0,
                    model TEXT DEFAULT '',
                    cost REAL DEFAULT 0.0,
                    error TEXT DEFAULT ''
                )
            """)
            await db.execute("""
                CREATE TABLE IF NOT EXISTS weaknesses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    category TEXT NOT NULL,
                    severity REAL DEFAULT 0.5,
                    description TEXT DEFAULT '',
                    sample_count INTEGER DEFAULT 0
                )
            """)
            await db.commit()
        self._initialized = True

    async def track_interaction(
        self,
        task_type: str = "general",
        success: bool = True,
        tokens: int = 0,
        latency_ms: int = 0,
        model: str = "",
        cost: float = 0.0,
        error: str = "",
    ) -> None:
        """Record a single interaction."""
        await self._ensure_db()
        import aiosqlite
        async with aiosqlite.connect(str(self.db_path)) as db:
            await db.execute(
                "INSERT INTO interactions (timestamp, task_type, success, tokens, latency_ms, model, cost, error) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (datetime.utcnow().isoformat(), task_type, int(success), tokens, latency_ms, model, cost, error),
            )
            await db.commit()

    async def get_metrics(self, days: int = 7) -> MetricsSummary:
        """Get summarized metrics for the last N days."""
        await self._ensure_db()
        import aiosqlite
        cutoff = (datetime.utcnow() - timedelta(days=days)).isoformat()
        async with aiosqlite.connect(str(self.db_path)) as db:
            async with db.execute(
                "SELECT COUNT(*), AVG(success), AVG(latency_ms), SUM(cost), SUM(tokens) FROM interactions WHERE timestamp > ?",
                (cutoff,),
            ) as cursor:
                row = await cursor.fetchone()
                if not row or row[0] == 0:
                    return MetricsSummary()
                return MetricsSummary(
                    total_interactions=row[0],
                    success_rate=float(row[1] or 0),
                    avg_latency_ms=float(row[2] or 0),
                    total_cost=float(row[3] or 0),
                    total_tokens=int(row[4] or 0),
                )

    async def diagnose(self, days: int = 7) -> list[Weakness]:
        """Analyze recent metrics AND user feedback to identify weaknesses.

        This merges two signals:
        1. System metrics (latency, success rate, cost) — objective
        2. User feedback (complaints, ratings, implicit signals) — subjective

        Feedback-derived weaknesses often surface problems metrics can't see:
        "the code compiled but was wrong" or "it didn't understand my question."
        """
        metrics = await self.get_metrics(days)
        weaknesses: list[Weakness] = []

        if metrics.total_interactions > 0:
            # Low success rate
            if metrics.success_rate < 0.8:
                weaknesses.append(Weakness(
                    category="reliability",
                    severity=1.0 - metrics.success_rate,
                    description=f"Low success rate: {metrics.success_rate:.1%}",
                    sample_count=metrics.total_interactions,
                ))

            # High latency
            if metrics.avg_latency_ms > 10000:
                weaknesses.append(Weakness(
                    category="performance",
                    severity=min(1.0, metrics.avg_latency_ms / 30000),
                    description=f"High average latency: {metrics.avg_latency_ms:.0f}ms",
                    sample_count=metrics.total_interactions,
                ))

            # High cost
            if metrics.total_cost > 1.0:
                cost_per = metrics.total_cost / metrics.total_interactions
                if cost_per > 0.05:
                    weaknesses.append(Weakness(
                        category="cost",
                        severity=min(1.0, cost_per / 0.20),
                        description=f"High cost per interaction: ${cost_per:.4f}",
                        sample_count=metrics.total_interactions,
                    ))

        # Merge user feedback into weakness diagnosis
        feedback_weaknesses = await self._diagnose_from_feedback(days)
        weaknesses.extend(feedback_weaknesses)

        # Deduplicate by category (keep the higher-severity one)
        seen: dict[str, Weakness] = {}
        for w in weaknesses:
            if w.category not in seen or w.severity > seen[w.category].severity:
                seen[w.category] = w
        weaknesses = list(seen.values())

        # Store weaknesses
        await self._ensure_db()
        import aiosqlite
        async with aiosqlite.connect(str(self.db_path)) as db:
            for w in weaknesses:
                await db.execute(
                    "INSERT INTO weaknesses (timestamp, category, severity, description, sample_count) VALUES (?, ?, ?, ?, ?)",
                    (datetime.utcnow().isoformat(), w.category, w.severity, w.description, w.sample_count),
                )
            await db.commit()

        return weaknesses

    async def _diagnose_from_feedback(self, days: int = 7) -> list[Weakness]:
        """Pull weaknesses from the user feedback system.

        This is the critical bridge: user complaints → Darwin evolution targets.
        """
        try:
            from pikaclaw.feedback.analyzer import FeedbackAnalyzer
            analyzer = FeedbackAnalyzer()
            return await analyzer.to_weaknesses(days=days, min_count=1)
        except Exception:
            return []

    async def get_hallucination_rate(self, days: int = 7) -> float:
        """Get hallucination rate (ratio of flagged responses)."""
        await self._ensure_db()
        import aiosqlite
        cutoff = (datetime.utcnow() - timedelta(days=days)).isoformat()
        async with aiosqlite.connect(str(self.db_path)) as db:
            async with db.execute(
                "SELECT COUNT(*) FROM interactions WHERE timestamp > ? AND error LIKE '%hallucin%'",
                (cutoff,),
            ) as cursor:
                flagged = (await cursor.fetchone())[0]
            async with db.execute(
                "SELECT COUNT(*) FROM interactions WHERE timestamp > ?",
                (cutoff,),
            ) as cursor:
                total = (await cursor.fetchone())[0]
        return flagged / total if total > 0 else 0.0
