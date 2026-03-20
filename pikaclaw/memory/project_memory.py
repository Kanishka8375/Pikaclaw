"""Project-level memory — facts and knowledge about the project."""
from __future__ import annotations
from pathlib import Path
from datetime import datetime


class ProjectMemory:
    """SQLite-backed project memory for facts and relationships."""

    def __init__(self):
        self.db_path = Path.home() / ".pikaclaw" / "memory" / "project.db"
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialized = False

    async def _ensure_db(self):
        if self._initialized:
            return
        import aiosqlite
        async with aiosqlite.connect(str(self.db_path)) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS facts (
                    key TEXT PRIMARY KEY,
                    value TEXT,
                    category TEXT DEFAULT 'general',
                    created_at TEXT,
                    updated_at TEXT
                )
            """)
            await db.commit()
        self._initialized = True

    async def remember(self, key: str, value: str, category: str = "general"):
        await self._ensure_db()
        import aiosqlite
        now = datetime.utcnow().isoformat()
        async with aiosqlite.connect(str(self.db_path)) as db:
            await db.execute(
                "INSERT OR REPLACE INTO facts (key, value, category, created_at, updated_at) VALUES (?, ?, ?, ?, ?)",
                (key, value, category, now, now),
            )
            await db.commit()

    async def recall(self, query: str, category: str | None = None) -> list[dict]:
        await self._ensure_db()
        import aiosqlite
        async with aiosqlite.connect(str(self.db_path)) as db:
            if category:
                sql = "SELECT key, value, category FROM facts WHERE category = ? AND (key LIKE ? OR value LIKE ?) LIMIT 20"
                params = (category, f"%{query}%", f"%{query}%")
            else:
                sql = "SELECT key, value, category FROM facts WHERE key LIKE ? OR value LIKE ? LIMIT 20"
                params = (f"%{query}%", f"%{query}%")
            async with db.execute(sql, params) as cursor:
                rows = await cursor.fetchall()
                return [{"key": r[0], "value": r[1], "category": r[2]} for r in rows]
