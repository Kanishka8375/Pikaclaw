"""Session persistence via SQLite."""
from __future__ import annotations
import json
from pathlib import Path
from datetime import datetime


class SessionManager:
    """Manages conversation sessions with SQLite persistence."""

    def __init__(self, config=None):
        self.db_path = Path.home() / ".pikaclaw" / "sessions" / "sessions.db"
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialized = False

    async def _ensure_db(self):
        if self._initialized:
            return
        import aiosqlite
        async with aiosqlite.connect(str(self.db_path)) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    id TEXT PRIMARY KEY,
                    created_at TEXT,
                    updated_at TEXT,
                    agent TEXT,
                    model TEXT,
                    messages TEXT,
                    metadata TEXT
                )
            """)
            await db.commit()
        self._initialized = True

    async def save_session(self, session_id: str, state) -> None:
        """Save session state to database."""
        await self._ensure_db()
        import aiosqlite
        now = datetime.utcnow().isoformat()
        async with aiosqlite.connect(str(self.db_path)) as db:
            await db.execute(
                "INSERT OR REPLACE INTO sessions (id, created_at, updated_at, agent, model, messages, metadata) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (session_id, now, now, state.active_agent, state.current_model or "",
                 json.dumps(state.messages[-50:]),  # Keep last 50 messages
                 json.dumps({"turns": state.turn_count, "tokens": state.total_input_tokens + state.total_output_tokens}))
            )
            await db.commit()

    async def load_session(self, session_id: str) -> dict | None:
        """Load a session by ID."""
        await self._ensure_db()
        import aiosqlite
        async with aiosqlite.connect(str(self.db_path)) as db:
            async with db.execute("SELECT * FROM sessions WHERE id = ?", (session_id,)) as cursor:
                row = await cursor.fetchone()
                if row:
                    return {
                        "id": row[0], "created_at": row[1], "updated_at": row[2],
                        "agent": row[3], "model": row[4],
                        "messages": json.loads(row[5]), "metadata": json.loads(row[6]),
                    }
        return None

    async def list_sessions(self, limit: int = 20) -> list[dict]:
        """List recent sessions."""
        await self._ensure_db()
        import aiosqlite
        async with aiosqlite.connect(str(self.db_path)) as db:
            async with db.execute("SELECT id, created_at, agent, model FROM sessions ORDER BY updated_at DESC LIMIT ?", (limit,)) as cursor:
                rows = await cursor.fetchall()
                return [{"id": r[0], "created_at": r[1], "agent": r[2], "model": r[3]} for r in rows]
