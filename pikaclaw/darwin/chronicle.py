"""Learning Chronicle — records experiments and lessons learned."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path


@dataclass
class Lesson:
    """A lesson learned from an experiment."""
    technique: str
    outcome: str
    lesson: str
    timestamp: str = ""


@dataclass
class ExperimentRecord:
    """A recorded experiment."""
    id: int = 0
    timestamp: str = ""
    hypothesis_summary: str = ""
    technique: str = ""
    verdict: str = ""
    improvement: float = 0.0
    lesson: str = ""


class LearningChronicle:
    """Stores experiment results and lessons for future reference."""

    def __init__(self, db_path: str | None = None):
        self.db_path = Path(db_path) if db_path else Path.home() / ".pikaclaw" / "darwin" / "chronicle.db"
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialized = False

    async def _ensure_db(self):
        if self._initialized:
            return
        import aiosqlite
        async with aiosqlite.connect(str(self.db_path)) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS experiments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    hypothesis_json TEXT DEFAULT '{}',
                    technique TEXT DEFAULT '',
                    verdict TEXT DEFAULT 'unknown',
                    improvement REAL DEFAULT 0.0,
                    lesson TEXT DEFAULT ''
                )
            """)
            await db.commit()
        self._initialized = True

    async def record(
        self,
        hypothesis: dict | None = None,
        technique: str = "",
        verdict: str = "unknown",
        improvement: float = 0.0,
        lesson: str = "",
    ) -> int:
        """Record an experiment result. Returns the experiment ID."""
        await self._ensure_db()
        import aiosqlite
        async with aiosqlite.connect(str(self.db_path)) as db:
            cursor = await db.execute(
                "INSERT INTO experiments (timestamp, hypothesis_json, technique, verdict, improvement, lesson) VALUES (?, ?, ?, ?, ?, ?)",
                (
                    datetime.utcnow().isoformat(),
                    json.dumps(hypothesis or {}),
                    technique,
                    verdict,
                    improvement,
                    lesson,
                ),
            )
            await db.commit()
            return cursor.lastrowid or 0

    async def get_lessons(self, category: str | None = None, limit: int = 20) -> list[Lesson]:
        """Get lessons from past experiments."""
        await self._ensure_db()
        import aiosqlite
        async with aiosqlite.connect(str(self.db_path)) as db:
            if category:
                sql = "SELECT technique, verdict, lesson, timestamp FROM experiments WHERE technique LIKE ? AND lesson != '' ORDER BY timestamp DESC LIMIT ?"
                params = (f"%{category}%", limit)
            else:
                sql = "SELECT technique, verdict, lesson, timestamp FROM experiments WHERE lesson != '' ORDER BY timestamp DESC LIMIT ?"
                params = (limit,)
            async with db.execute(sql, params) as cursor:
                rows = await cursor.fetchall()
                return [Lesson(technique=r[0], outcome=r[1], lesson=r[2], timestamp=r[3]) for r in rows]

    async def get_technique_success_rate(self, technique: str) -> float:
        """Get the success rate for a specific technique."""
        await self._ensure_db()
        import aiosqlite
        async with aiosqlite.connect(str(self.db_path)) as db:
            async with db.execute(
                "SELECT COUNT(*), SUM(CASE WHEN verdict = 'pass' THEN 1 ELSE 0 END) FROM experiments WHERE technique = ?",
                (technique,),
            ) as cursor:
                row = await cursor.fetchone()
                if not row or row[0] == 0:
                    return 0.0
                return float(row[1] or 0) / row[0]

    async def get_history(self, limit: int = 20) -> list[ExperimentRecord]:
        """Get recent experiment history."""
        await self._ensure_db()
        import aiosqlite
        async with aiosqlite.connect(str(self.db_path)) as db:
            async with db.execute(
                "SELECT id, timestamp, hypothesis_json, technique, verdict, improvement, lesson FROM experiments ORDER BY timestamp DESC LIMIT ?",
                (limit,),
            ) as cursor:
                rows = await cursor.fetchall()
                results = []
                for r in rows:
                    hyp = json.loads(r[2]) if r[2] else {}
                    results.append(ExperimentRecord(
                        id=r[0], timestamp=r[1],
                        hypothesis_summary=hyp.get("description", "")[:200],
                        technique=r[3], verdict=r[4],
                        improvement=r[5], lesson=r[6],
                    ))
                return results
