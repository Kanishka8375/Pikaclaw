"""Embedding-based semantic search — stub using text similarity."""
from __future__ import annotations


class EmbeddingSearch:
    """Simple text-based search (placeholder for real embeddings)."""

    def __init__(self):
        self._store: list[dict] = []

    def add(self, text: str, metadata: dict | None = None):
        self._store.append({"text": text, "metadata": metadata or {}})

    def search(self, query: str, top_k: int = 5) -> list[dict]:
        """Simple keyword overlap search."""
        query_words = set(query.lower().split())
        scored = []
        for item in self._store:
            item_words = set(item["text"].lower().split())
            overlap = len(query_words & item_words)
            if overlap > 0:
                scored.append((overlap, item))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [s[1] for s in scored[:top_k]]
