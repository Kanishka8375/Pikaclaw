"""PII detection and redaction."""
from __future__ import annotations
import re

PATTERNS = {
    "email": r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
    "phone": r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
    "ssn": r'\b\d{3}-\d{2}-\d{4}\b',
    "credit_card": r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b',
    "ip_address": r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b',
}

_compiled = {k: re.compile(v) for k, v in PATTERNS.items()}


class PIIRedactor:
    """Detects and redacts PII from text."""

    def redact(self, text: str) -> tuple[str, list[dict]]:
        """Redact PII. Returns (redacted_text, found_entities)."""
        entities = []
        for pii_type, pattern in _compiled.items():
            for match in pattern.finditer(text):
                entities.append({"type": pii_type, "start": match.start(), "end": match.end()})
            placeholder = f"{{{{{pii_type.upper()}_REDACTED}}}}"
            text = pattern.sub(placeholder, text)
        return text, entities

    def has_pii(self, text: str) -> bool:
        for pattern in _compiled.values():
            if pattern.search(text):
                return True
        return False
