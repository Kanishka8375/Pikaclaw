"""FeedbackCollector — stores explicit and implicit user feedback in SQLite.

This is the single source of truth for "what went wrong."
Darwin reads this to decide what to evolve.

Feedback categories:
    wrong_answer    — factually incorrect, hallucinated, or irrelevant
    misunderstood   — didn't understand what user wanted
    incomplete      — answer was partial, missing steps
    slow            — took too long, too many turns
    tool_failure    — tool crashed, wrong tool used, permission denied
    bad_code        — code had bugs, didn't compile, wrong approach
    hallucination   — made up files, functions, or facts
    repetitive      — looped, repeated itself, went in circles
    unsafe          — did something dangerous or leaked secrets
    other           — catch-all
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from uuid import uuid4

CATEGORIES = frozenset({
    "wrong_answer", "misunderstood", "incomplete", "slow",
    "tool_failure", "bad_code", "hallucination", "repetitive",
    "unsafe", "other",
})


@dataclass
class FeedbackEntry:
    """A single feedback record."""
    id: str = ""
    timestamp: str = ""
    session_id: str = ""
    rating: int = 0              # 1-5 (1=terrible, 5=great) or 0=unrated
    category: str = "other"
    comment: str = ""
    agent: str = ""
    model: str = ""
    turn_count: int = 0
    conversation_snippet: str = ""  # last few messages for context
    source: str = "explicit"     # "explicit" | "implicit"
    resolved: bool = False
    resolution_id: str = ""      # darwin experiment ID that addressed this


class FeedbackCollector:
    """Collects and stores user feedback in SQLite.

    Two kinds of feedback flow here:
    1. Explicit: user types /feedback, rates response, picks category
    2. Implicit: detected automatically by ImplicitSignalDetector
    """

    def __init__(self, db_path: str | None = None):
        self.db_path = Path(db_path) if db_path else Path.home() / ".pikaclaw" / "feedback" / "feedback.db"
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialized = False

    async def _ensure_db(self):
        if self._initialized:
            return
        import aiosqlite
        async with aiosqlite.connect(str(self.db_path)) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS feedback (
                    id TEXT PRIMARY KEY,
                    timestamp TEXT NOT NULL,
                    session_id TEXT DEFAULT '',
                    rating INTEGER DEFAULT 0,
                    category TEXT DEFAULT 'other',
                    comment TEXT DEFAULT '',
                    agent TEXT DEFAULT '',
                    model TEXT DEFAULT '',
                    turn_count INTEGER DEFAULT 0,
                    conversation_snippet TEXT DEFAULT '',
                    source TEXT DEFAULT 'explicit',
                    resolved INTEGER DEFAULT 0,
                    resolution_id TEXT DEFAULT ''
                )
            """)
            await db.execute("""
                CREATE INDEX IF NOT EXISTS idx_feedback_category ON feedback(category)
            """)
            await db.execute("""
                CREATE INDEX IF NOT EXISTS idx_feedback_timestamp ON feedback(timestamp)
            """)
            await db.execute("""
                CREATE INDEX IF NOT EXISTS idx_feedback_resolved ON feedback(resolved)
            """)
            await db.commit()
        self._initialized = True

    async def submit(
        self,
        rating: int = 0,
        category: str = "other",
        comment: str = "",
        session_id: str = "",
        agent: str = "",
        model: str = "",
        turn_count: int = 0,
        conversation_snippet: str = "",
        source: str = "explicit",
    ) -> str:
        """Submit feedback. Returns the feedback ID."""
        await self._ensure_db()

        # Validate
        if category not in CATEGORIES:
            category = "other"
        rating = max(0, min(5, rating))

        entry_id = str(uuid4())[:12]
        import aiosqlite
        async with aiosqlite.connect(str(self.db_path)) as db:
            await db.execute(
                """INSERT INTO feedback
                   (id, timestamp, session_id, rating, category, comment, agent, model,
                    turn_count, conversation_snippet, source, resolved, resolution_id)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0, '')""",
                (entry_id, datetime.utcnow().isoformat(), session_id, rating, category,
                 comment, agent, model, turn_count, conversation_snippet[:2000], source),
            )
            await db.commit()
        return entry_id

    async def get_unresolved(self, limit: int = 50) -> list[FeedbackEntry]:
        """Get unresolved feedback, newest first. This is what Darwin reads."""
        await self._ensure_db()
        import aiosqlite
        async with aiosqlite.connect(str(self.db_path)) as db:
            async with db.execute(
                "SELECT * FROM feedback WHERE resolved = 0 ORDER BY timestamp DESC LIMIT ?",
                (limit,),
            ) as cursor:
                rows = await cursor.fetchall()
                return [self._row_to_entry(r) for r in rows]

    async def get_by_category(self, category: str, limit: int = 50) -> list[FeedbackEntry]:
        """Get feedback filtered by category."""
        await self._ensure_db()
        import aiosqlite
        async with aiosqlite.connect(str(self.db_path)) as db:
            async with db.execute(
                "SELECT * FROM feedback WHERE category = ? ORDER BY timestamp DESC LIMIT ?",
                (category, limit),
            ) as cursor:
                rows = await cursor.fetchall()
                return [self._row_to_entry(r) for r in rows]

    async def get_recent(self, days: int = 7, limit: int = 100) -> list[FeedbackEntry]:
        """Get recent feedback."""
        await self._ensure_db()
        from datetime import timedelta
        import aiosqlite
        cutoff = (datetime.utcnow() - timedelta(days=days)).isoformat()
        async with aiosqlite.connect(str(self.db_path)) as db:
            async with db.execute(
                "SELECT * FROM feedback WHERE timestamp > ? ORDER BY timestamp DESC LIMIT ?",
                (cutoff, limit),
            ) as cursor:
                rows = await cursor.fetchall()
                return [self._row_to_entry(r) for r in rows]

    async def mark_resolved(self, feedback_id: str, resolution_id: str = "") -> bool:
        """Mark feedback as resolved (addressed by Darwin or manually)."""
        await self._ensure_db()
        import aiosqlite
        async with aiosqlite.connect(str(self.db_path)) as db:
            cursor = await db.execute(
                "UPDATE feedback SET resolved = 1, resolution_id = ? WHERE id = ?",
                (resolution_id, feedback_id),
            )
            await db.commit()
            return cursor.rowcount > 0

    async def get_satisfaction_score(self, days: int = 7) -> dict:
        """Compute satisfaction metrics over a time window."""
        await self._ensure_db()
        from datetime import timedelta
        import aiosqlite
        cutoff = (datetime.utcnow() - timedelta(days=days)).isoformat()
        async with aiosqlite.connect(str(self.db_path)) as db:
            # Total feedback count
            async with db.execute(
                "SELECT COUNT(*) FROM feedback WHERE timestamp > ?", (cutoff,)
            ) as cursor:
                total = (await cursor.fetchone())[0]

            # Average rating (only rated entries)
            async with db.execute(
                "SELECT AVG(rating) FROM feedback WHERE timestamp > ? AND rating > 0", (cutoff,)
            ) as cursor:
                avg_rating = (await cursor.fetchone())[0] or 0.0

            # Category breakdown
            async with db.execute(
                "SELECT category, COUNT(*) FROM feedback WHERE timestamp > ? GROUP BY category ORDER BY COUNT(*) DESC",
                (cutoff,),
            ) as cursor:
                categories = {r[0]: r[1] for r in await cursor.fetchall()}

            # Resolution rate
            async with db.execute(
                "SELECT COUNT(*) FROM feedback WHERE timestamp > ? AND resolved = 1", (cutoff,)
            ) as cursor:
                resolved = (await cursor.fetchone())[0]

            # Implicit vs explicit
            async with db.execute(
                "SELECT source, COUNT(*) FROM feedback WHERE timestamp > ? GROUP BY source",
                (cutoff,),
            ) as cursor:
                sources = {r[0]: r[1] for r in await cursor.fetchall()}

        return {
            "total_feedback": total,
            "avg_rating": round(avg_rating, 2),
            "resolution_rate": round(resolved / total, 2) if total > 0 else 0.0,
            "category_breakdown": categories,
            "source_breakdown": sources,
            "top_complaint": max(categories, key=categories.get) if categories else None,
            "days": days,
        }

    def _row_to_entry(self, row) -> FeedbackEntry:
        return FeedbackEntry(
            id=row[0], timestamp=row[1], session_id=row[2],
            rating=row[3], category=row[4], comment=row[5],
            agent=row[6], model=row[7], turn_count=row[8],
            conversation_snippet=row[9], source=row[10],
            resolved=bool(row[11]), resolution_id=row[12],
        )
