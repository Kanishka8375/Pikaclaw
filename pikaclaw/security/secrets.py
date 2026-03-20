"""Secret sanitization — prevents API keys and credentials from leaking."""
from __future__ import annotations
import re


class SecretSanitizer:
    """Detects and redacts secrets from text."""

    PATTERNS: list[tuple[str, str]] = [
        (r'sk-ant-[a-zA-Z0-9_-]{10,}', '{{ANTHROPIC_KEY}}'),
        (r'sk-or-[a-zA-Z0-9_-]{10,}', '{{OPENROUTER_KEY}}'),
        (r'sk-[a-zA-Z0-9]{20,}', '{{OPENAI_KEY}}'),
        (r'ghp_[a-zA-Z0-9]{10,}', '{{GITHUB_TOKEN}}'),
        (r'gho_[a-zA-Z0-9]{10,}', '{{GITHUB_OAUTH}}'),
        (r'github_pat_[a-zA-Z0-9_]{20,}', '{{GITHUB_PAT}}'),
        (r'AGE-SECRET-KEY-[A-Z0-9]+', '{{AGE_KEY}}'),
        (r'AKIA[0-9A-Z]{16}', '{{AWS_KEY}}'),
        (r'(?:password|passwd|pwd)\s*[=:]\s*\S+', '{{PASSWORD_REDACTED}}'),
        (r'[A-Za-z0-9+/]{40,}={0,2}', '{{BASE64_REDACTED}}'),
    ]

    def __init__(self):
        self._compiled = [(re.compile(p), r) for p, r in self.PATTERNS]

    def sanitize(self, text: str) -> str:
        """Replace all detected secrets with placeholders."""
        for pattern, replacement in self._compiled:
            text = pattern.sub(replacement, text)
        return text

    def has_secrets(self, text: str) -> bool:
        """Check if text contains any detected secrets."""
        for pattern, _ in self._compiled:
            if pattern.search(text):
                return True
        return False
