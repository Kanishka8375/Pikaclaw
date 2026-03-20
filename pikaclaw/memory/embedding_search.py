"""Embedding-based semantic search with Ollama fallback to TF-IDF."""
from __future__ import annotations

import math
from collections import Counter


class EmbeddingSearch:
    """Semantic search using embeddings (Ollama) or text similarity (fallback)."""

    def __init__(self, ollama_url: str = "http://localhost:11434"):
        self.ollama_url = ollama_url
        self._store: list[dict] = []

    def add(self, text: str, metadata: dict | None = None) -> None:
        """Add a document to the search index."""
        self._store.append({"text": text, "metadata": metadata or {}})

    async def embed(self, text: str) -> list[float]:
        """Get embeddings from Ollama, falling back to simple TF-IDF vector."""
        try:
            import httpx
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.post(
                    f"{self.ollama_url}/api/embeddings",
                    json={"model": "nomic-embed-text", "prompt": text},
                )
                if response.status_code == 200:
                    return response.json().get("embedding", [])
        except Exception:
            pass

        # Fallback: simple word frequency vector
        return self._tfidf_vector(text)

    def _tfidf_vector(self, text: str) -> list[float]:
        """Simple TF-IDF-like vector from word frequencies."""
        words = text.lower().split()
        counts = Counter(words)
        vocab = self._get_vocab()
        if not vocab:
            vocab = sorted(set(words))
        return [float(counts.get(w, 0)) for w in vocab]

    def _get_vocab(self) -> list[str]:
        """Build vocabulary from all stored documents."""
        all_words: set[str] = set()
        for item in self._store:
            all_words.update(item["text"].lower().split())
        return sorted(all_words)

    @staticmethod
    def cosine_similarity(a: list[float], b: list[float]) -> float:
        """Compute cosine similarity between two vectors."""
        if not a or not b:
            return 0.0
        max_len = max(len(a), len(b))
        a = a + [0.0] * (max_len - len(a))
        b = b + [0.0] * (max_len - len(b))

        dot = sum(x * y for x, y in zip(a, b))
        norm_a = math.sqrt(sum(x * x for x in a))
        norm_b = math.sqrt(sum(x * x for x in b))
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return dot / (norm_a * norm_b)

    def search(self, query: str, top_k: int = 5) -> list[dict]:
        """Search using keyword overlap (synchronous)."""
        query_words = set(query.lower().split())
        scored = []
        for item in self._store:
            item_words = set(item["text"].lower().split())
            overlap = len(query_words & item_words)
            if overlap > 0:
                scored.append((overlap, item))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [s[1] for s in scored[:top_k]]

    async def async_search(self, query: str, documents: list[str] | None = None, top_k: int = 5) -> list[tuple[int, float]]:
        """Search using embeddings. Returns list of (index, similarity) tuples."""
        docs = documents or [item["text"] for item in self._store]
        if not docs:
            return []

        query_vec = await self.embed(query)
        results: list[tuple[int, float]] = []

        for i, doc in enumerate(docs):
            doc_vec = await self.embed(doc)
            sim = self.cosine_similarity(query_vec, doc_vec)
            results.append((i, sim))

        results.sort(key=lambda x: x[1], reverse=True)
        return results[:top_k]
