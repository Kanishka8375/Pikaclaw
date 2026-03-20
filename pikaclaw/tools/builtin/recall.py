"""Recall tool — search memories in SQLite."""
from __future__ import annotations

from pathlib import Path


DB_PATH = Path.home() / ".pikaclaw" / "memory.db"


class RecallTool:
    """Search persistent memory by keyword."""

    name = "Recall"
    description = "Search stored memories by keyword (searches key and value)."
    parameters = {
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "Keyword to search for in memories."},
            "category": {"type": "string", "description": "Optional category to filter by."},
        },
        "required": ["query"],
    }

    async def execute(self, params: dict) -> str:
        try:
            import aiosqlite
        except ImportError:
            return "Error: aiosqlite is not installed. Run: pip install aiosqlite"

        try:
            query = params["query"]
            category = params.get("category")

            if not DB_PATH.exists():
                return "No memories stored yet."

            async with aiosqlite.connect(str(DB_PATH)) as db:
                if category:
                    cursor = await db.execute(
                        "SELECT key, value, category, timestamp FROM memories "
                        "WHERE (key LIKE ? OR value LIKE ?) AND category = ? "
                        "ORDER BY timestamp DESC",
                        (f"%{query}%", f"%{query}%", category),
                    )
                else:
                    cursor = await db.execute(
                        "SELECT key, value, category, timestamp FROM memories "
                        "WHERE key LIKE ? OR value LIKE ? "
                        "ORDER BY timestamp DESC",
                        (f"%{query}%", f"%{query}%"),
                    )

                rows = await cursor.fetchall()

            if not rows:
                return "No matching memories found."

            results = []
            for key, value, cat, ts in rows:
                results.append(f"[{cat}] {key}: {value}  (saved: {ts})")
            return "\n".join(results)
        except Exception as e:
            return f"Error in recall: {e}"
