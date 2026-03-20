"""Prompt injection defense."""
from __future__ import annotations
import re


INJECTION_PATTERNS = [
    r"ignore\s+(all\s+)?previous\s+instructions",
    r"ignore\s+the\s+above",
    r"disregard\s+(all\s+)?prior",
    r"you\s+are\s+now\s+a",
    r"new\s+system\s+prompt",
    r"<\|im_start\|>",
    r"<\|im_end\|>",
    r"\[INST\]",
    r"\[/INST\]",
    r"<<SYS>>",
    r"system:\s*you\s+are",
    r"ADMIN\s*OVERRIDE",
    r"SUDO\s+MODE",
]

_compiled_injections = [re.compile(p, re.IGNORECASE) for p in INJECTION_PATTERNS]


class PromptInjectionDefense:
    """Multi-layer prompt injection defense."""

    def __init__(self):
        self.canary: str | None = None

    def set_canary(self, canary: str):
        """Set a canary token to detect leakage."""
        self.canary = canary

    def check_input(self, text: str) -> tuple[bool, str]:
        """Check user input for injection attempts. Returns (is_safe, reason)."""
        for pattern in _compiled_injections:
            match = pattern.search(text)
            if match:
                return False, f"Potential prompt injection detected: '{match.group()}'"
        return True, ""

    def wrap_untrusted(self, text: str) -> str:
        """Wrap untrusted content with spotlighting tags."""
        return f"<UNTRUSTED_DATA>\n{text}\n</UNTRUSTED_DATA>"

    def check_output(self, text: str) -> tuple[bool, str]:
        """Check model output for suspicious patterns."""
        # Check canary leakage
        if self.canary and self.canary in text:
            return False, "Canary token leaked in output"
        # Check for dangerous shell commands in output
        dangerous = [r"rm\s+-rf\s+/", r"sudo\s+rm", r">\s*/dev/sd"]
        for pattern in dangerous:
            if re.search(pattern, text, re.IGNORECASE):
                return False, f"Dangerous command pattern in output: {pattern}"
        return True, ""

    def check_code(self, code: str) -> tuple[bool, list[str]]:
        """Scan generated code for dangerous patterns."""
        issues = []
        dangerous_patterns = [
            (r'\beval\s*\(', "Use of eval()"),
            (r'\bexec\s*\(', "Use of exec()"),
            (r'subprocess.*shell\s*=\s*True', "subprocess with shell=True"),
            (r'os\.system\s*\(', "Use of os.system()"),
            (r'__import__\s*\(', "Dynamic import"),
        ]
        for pattern, desc in dangerous_patterns:
            if re.search(pattern, code):
                issues.append(desc)
        return len(issues) == 0, issues
