"""Context window management."""
from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pikaclaw.config.schema import PikaClawConfig


class ContextManager:
    """Manages conversation context window usage."""

    def __init__(self, config: PikaClawConfig | None = None):
        self.config = config
        self.max_tokens = 128000  # default context window
        self._token_count = 0

    def estimate_tokens(self, text: str) -> int:
        """Rough token estimate: ~4 chars per token."""
        return max(1, len(text) // 4)

    def track_message(self, message: dict) -> int:
        """Track a message's token count. Returns tokens used."""
        content = message.get("content", "")
        if isinstance(content, list):
            content = " ".join(str(c) for c in content)
        tokens = self.estimate_tokens(str(content))
        self._token_count += tokens
        return tokens

    @property
    def usage_percent(self) -> float:
        return min(100.0, (self._token_count / self.max_tokens) * 100)

    def needs_compaction(self) -> bool:
        return self.usage_percent >= 92.0

    def reset(self):
        self._token_count = 0
