"""Darwin constraints — safety rules for self-evolution."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from fnmatch import fnmatch


@dataclass
class ValidationResult:
    """Result of constraint validation."""
    passed: bool
    violations: list[str] = field(default_factory=list)


@dataclass
class CodePatch:
    """A code patch produced by the forge."""
    files: dict[str, str] = field(default_factory=dict)
    tests: dict[str, str] = field(default_factory=dict)
    metadata: dict = field(default_factory=dict)

    @property
    def total_lines(self) -> int:
        return sum(c.count("\n") + 1 for c in self.files.values())


class DarwinConstraints:
    """Safety constraints that Darwin may never violate."""

    FORBIDDEN_PATHS: frozenset[str] = frozenset({
        "pikaclaw/security/*",
        "pikaclaw/darwin/constraints.py",
        "pikaclaw/darwin/watchdog.py",
        ".pikaclaw/audit.log",
        "pyproject.toml",
    })

    MAX_PATCH_SIZE: int = 2000
    MAX_FILES_MODIFIED: int = 20
    MAX_PATCHES_PER_DAY: int = 5

    FORBIDDEN_PATTERNS: list[str] = [
        r"os\.system\(",
        r"\beval\(",
        r"\bexec\(",
        r"__import__\(",
        r"subprocess\.Popen\(.*shell\s*=\s*True",
        r"open\(['\"]\/etc\/",
        r"open\(['\"]\/dev\/",
        r"shutil\.rmtree\(['\"]\/",
    ]

    def __init__(self):
        self._compiled_patterns = [re.compile(p) for p in self.FORBIDDEN_PATTERNS]

    def is_forbidden_path(self, path: str) -> bool:
        """Check if a file path is protected from modification."""
        normalized = path.replace("\\", "/")
        for pattern in self.FORBIDDEN_PATHS:
            if fnmatch(normalized, pattern):
                return True
        return False

    def validate_patch(self, patch: CodePatch) -> ValidationResult:
        """Validate a code patch against all constraints."""
        violations: list[str] = []

        # Check total size
        if patch.total_lines > self.MAX_PATCH_SIZE:
            violations.append(f"Patch too large: {patch.total_lines} lines (max {self.MAX_PATCH_SIZE})")

        # Check file count
        if len(patch.files) > self.MAX_FILES_MODIFIED:
            violations.append(f"Too many files: {len(patch.files)} (max {self.MAX_FILES_MODIFIED})")

        # Check forbidden paths
        for file_path in patch.files:
            if self.is_forbidden_path(file_path):
                violations.append(f"Forbidden path: {file_path}")

        # Check forbidden patterns in code
        for file_path, content in patch.files.items():
            for pattern in self._compiled_patterns:
                matches = pattern.findall(content)
                if matches:
                    violations.append(f"Forbidden pattern in {file_path}: {matches[0]}")

        return ValidationResult(passed=len(violations) == 0, violations=violations)
