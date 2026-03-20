"""Context compaction — summarize old messages to save tokens."""
from __future__ import annotations


class ContextCompactor:
    """Compacts conversation context by summarizing older messages."""

    def compact(self, messages: list[dict], keep_recent: int = 10) -> list[dict]:
        """Summarize older messages, keep recent ones intact."""
        if len(messages) <= keep_recent:
            return messages

        old = messages[:-keep_recent]
        recent = messages[-keep_recent:]

        # Build summary of old messages
        summary_parts = []
        for msg in old:
            role = msg.get("role", "unknown")
            content = str(msg.get("content", ""))[:200]
            if role == "user":
                summary_parts.append(f"User asked: {content}")
            elif role == "assistant":
                summary_parts.append(f"Assistant: {content}")
            elif role == "tool":
                summary_parts.append(f"Tool {msg.get('name', '?')}: {content[:100]}")

        summary = "\n".join(summary_parts[-20:])  # Keep last 20 summaries
        summary_msg = {
            "role": "user",
            "content": f"[Context Summary of {len(old)} earlier messages]:\n{summary}\n[End Summary]"
        }

        return [summary_msg] + recent
