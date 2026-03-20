"""Remember tool — store memories in SQLite."""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path


DB_PATH = Path.home() / ".pikaclaw" / "memory.db"


class RememberTool:
    """Store a key-value memory in persistent storage."""

    name = "Remember"
    description = "Store a key-value pair in persistent memory (SQLite)."
    parameters = {
        "type": "object",
        "properties": {
            "key": {"type": "string", "description": "The memory key/name."},
            "value": {"type": "string", "description": "The value to remember."},
            "category": {"type": "string", "description": "Category for organization.", "default": "general"},
        },
        "required": ["key", "value"],
    }

    async def execute(self, params: dict) -> str:
        try:
            import aiosqlite
        except ImportError:
            return "Error: aiosqlite is not installed. Run: pip install aiosqlite"

        try:
            key = params["key"]
            value = params["value"]
            category = params.get("category", "general")
            timestamp = datetime.now(timezone.utc).isoformat()

            DB_PATH.parent.mkdir(parents=True, exist_ok=True)

            async with aiosqlite.connect(str(DB_PATH)) as db:
                await db.execute(
                    "CREATE TABLE IF NOT EXISTS memories "
                    "(key TEXT, value TEXT, category TEXT, timestamp TEXT)"
                )
                # Upsert: delete old entry with same key+category, then insert
                await db.execute(
                    "DELETE FROM memories WHERE key = ? AND category = ?",
                    (key, category),
                )
                await db.execute(
                    "INSERT INTO memories (key, value, category, timestamp) VALUES (?, ?, ?, ?)",
                    (key, value, category, timestamp),
                )
                await db.commit()

            return f"Remembered '{key}' in category '{category}'."
        except Exception as e:
            return f"Error in remember: {e}"
