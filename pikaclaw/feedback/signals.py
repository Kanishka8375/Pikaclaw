"""ImplicitSignalDetector — detects user dissatisfaction without explicit feedback.

The idea: users don't always type /feedback. But their BEHAVIOR tells you
when something went wrong. This module watches conversation patterns and
automatically generates feedback entries when frustration signals appear.

Signals detected:
    retry           — user re-asks the same question (similarity > 0.7)
    rejection       — user says "no", "wrong", "that's not right", "try again"
    abandonment     — user starts a completely new topic mid-task (topic shift)
    correction      — user manually provides the correct answer after AI failed
    agent_switch    — user switches agents (current one wasn't working)
    long_struggle   — many turns (>10) without a "done" signal
    error_cascade   — 3+ tool errors in a row
    undo_after_edit — user undoes the AI's edit (implying it was wrong)
"""
from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass
class ImplicitSignal:
    """A detected implicit frustration signal."""
    signal_type: str
    confidence: float   # 0.0 - 1.0
    category: str       # maps to FeedbackCollector categories
    description: str
    evidence: str = ""  # the user message or pattern that triggered it


# Words/phrases that signal explicit rejection
_REJECTION_PATTERNS = [
    r"\b(?:no|nope|wrong|incorrect|that'?s?\s*not\s*(?:right|correct|what))\b",
    r"\b(?:try\s*again|redo|undo\s*that|revert|go\s*back)\b",
    r"\b(?:you'?re?\s*wrong|that'?s?\s*(?:wrong|bad|broken|terrible))\b",
    r"\b(?:doesn'?t?\s*work|didn'?t?\s*work|not\s*working|still\s*(?:broken|wrong))\b",
    r"\b(?:i\s*(?:said|asked|meant|wanted)|that'?s?\s*not\s*what\s*i)\b",
    r"\b(?:stop|halt|cancel|never\s*mind|forget\s*it)\b",
]

# Words that signal the user is providing a correction
_CORRECTION_PATTERNS = [
    r"\b(?:actually|the\s*correct\s*(?:answer|way)|it\s*should\s*be)\b",
    r"\b(?:no,?\s*(?:it'?s?|the|you\s*need))\b",
    r"\b(?:let\s*me\s*(?:clarify|explain|rephrase))\b",
    r"\b(?:what\s*i\s*(?:meant|want(?:ed)?))\b",
]

_COMPILED_REJECTIONS = [re.compile(p, re.IGNORECASE) for p in _REJECTION_PATTERNS]
_COMPILED_CORRECTIONS = [re.compile(p, re.IGNORECASE) for p in _CORRECTION_PATTERNS]


class ImplicitSignalDetector:
    """Watches conversation flow and detects frustration without explicit feedback.

    Call `analyze_message()` on every user message. It returns a list of
    detected signals (usually 0 or 1). Feed these into FeedbackCollector.submit()
    with source="implicit".
    """

    def __init__(self):
        self._recent_user_messages: list[str] = []
        self._recent_errors: int = 0
        self._turn_count: int = 0
        self._last_agent: str = ""
        self._task_started: bool = False

    def analyze_message(self, user_message: str, context: dict | None = None) -> list[ImplicitSignal]:
        """Analyze a user message for implicit frustration signals.

        Args:
            user_message: The raw user input
            context: Optional dict with keys: agent, turn_count, last_tool_error,
                     last_response, agent_switched
        """
        ctx = context or {}
        signals: list[ImplicitSignal] = []
        msg_lower = user_message.lower().strip()

        # Signal 1: Rejection language
        rejection = self._detect_rejection(msg_lower, user_message)
        if rejection:
            signals.append(rejection)

        # Signal 2: Correction language
        correction = self._detect_correction(msg_lower, user_message)
        if correction:
            signals.append(correction)

        # Signal 3: Retry (similar to previous message)
        retry = self._detect_retry(msg_lower)
        if retry:
            signals.append(retry)

        # Signal 4: Agent switch (user switched agents)
        if ctx.get("agent_switched"):
            signals.append(ImplicitSignal(
                signal_type="agent_switch",
                confidence=0.6,
                category="misunderstood",
                description=f"User switched from {ctx.get('previous_agent', '?')} to {ctx.get('agent', '?')}",
                evidence=f"Agent change: {ctx.get('previous_agent')} → {ctx.get('agent')}",
            ))

        # Signal 5: Long struggle (many turns)
        turn_count = ctx.get("turn_count", 0)
        if turn_count > 10 and turn_count % 5 == 0:
            signals.append(ImplicitSignal(
                signal_type="long_struggle",
                confidence=min(0.9, 0.4 + (turn_count - 10) * 0.05),
                category="incomplete",
                description=f"Conversation reached {turn_count} turns — possible struggle",
                evidence=f"Turn count: {turn_count}",
            ))

        # Signal 6: Error cascade (tool errors piling up)
        if ctx.get("last_tool_error"):
            self._recent_errors += 1
            if self._recent_errors >= 3:
                signals.append(ImplicitSignal(
                    signal_type="error_cascade",
                    confidence=0.8,
                    category="tool_failure",
                    description=f"{self._recent_errors} consecutive tool errors",
                    evidence=str(ctx.get("last_tool_error", ""))[:200],
                ))
        else:
            self._recent_errors = 0

        # Track message history for retry detection
        self._recent_user_messages.append(msg_lower)
        if len(self._recent_user_messages) > 20:
            self._recent_user_messages = self._recent_user_messages[-20:]

        return signals

    def _detect_rejection(self, msg_lower: str, original: str) -> ImplicitSignal | None:
        """Detect rejection language."""
        # Don't flag very long messages — those are usually new instructions, not rejections
        if len(msg_lower) > 200:
            return None

        for pattern in _COMPILED_REJECTIONS:
            match = pattern.search(msg_lower)
            if match:
                return ImplicitSignal(
                    signal_type="rejection",
                    confidence=0.75,
                    category="wrong_answer",
                    description=f"User rejected response: '{match.group()}'",
                    evidence=original[:200],
                )
        return None

    def _detect_correction(self, msg_lower: str, original: str) -> ImplicitSignal | None:
        """Detect correction language (user providing the right answer)."""
        for pattern in _COMPILED_CORRECTIONS:
            match = pattern.search(msg_lower)
            if match:
                return ImplicitSignal(
                    signal_type="correction",
                    confidence=0.65,
                    category="wrong_answer",
                    description=f"User correcting AI: '{match.group()}'",
                    evidence=original[:200],
                )
        return None

    def _detect_retry(self, msg_lower: str) -> ImplicitSignal | None:
        """Detect if user is retrying a previous question."""
        if len(self._recent_user_messages) < 1:
            return None

        # Compare with recent messages (skip the current one, which isn't appended yet)
        for prev in self._recent_user_messages[-5:]:
            similarity = self._word_overlap(msg_lower, prev)
            if similarity > 0.7 and similarity < 1.0:  # High overlap but not identical
                return ImplicitSignal(
                    signal_type="retry",
                    confidence=similarity,
                    category="wrong_answer",
                    description="User retrying a similar question",
                    evidence=f"Current: '{msg_lower[:100]}' | Previous: '{prev[:100]}'",
                )
        return None

    @staticmethod
    def _word_overlap(a: str, b: str) -> float:
        """Compute word-level Jaccard similarity between two strings."""
        words_a = set(a.split())
        words_b = set(b.split())
        if not words_a or not words_b:
            return 0.0
        intersection = len(words_a & words_b)
        union = len(words_a | words_b)
        return intersection / union if union > 0 else 0.0

    def reset(self):
        """Reset detector state (e.g., on /clear)."""
        self._recent_user_messages.clear()
        self._recent_errors = 0
        self._turn_count = 0
        self._task_started = False
