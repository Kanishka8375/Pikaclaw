"""Sentinel — protects critical files from modification."""
from __future__ import annotations
import fnmatch
import hashlib
from pathlib import Path


PROTECTED_PATTERNS = [
    "pikaclaw/security/*",
    "pikaclaw/security/**/*",
    ".pikaclaw/audit.log",
    ".pikaclaw/audit.jsonl",
]


class Sentinel:
    """Guards protected files and monitors integrity."""

    def __init__(self, extra_patterns: list[str] | None = None):
        self.patterns = list(PROTECTED_PATTERNS)
        if extra_patterns:
            self.patterns.extend(extra_patterns)
        self._hashes: dict[str, str] = {}

    def is_protected_path(self, path: str) -> bool:
        """Check if a file path matches any protected pattern."""
        # Normalize path
        path = path.replace("\\", "/")
        for pattern in self.patterns:
            if fnmatch.fnmatch(path, pattern):
                return True
        # Also check if it's under pikaclaw/security/ directory
        if "pikaclaw/security/" in path or path.startswith("pikaclaw/security/"):
            return True
        return False

    def block_if_protected(self, path: str) -> None:
        """Raise error if path is protected."""
        if self.is_protected_path(path):
            raise PermissionError(f"Protected file cannot be modified: {path}")

    def compute_hash(self, file_path: str) -> str:
        """Compute SHA-256 hash of a file."""
        p = Path(file_path)
        if not p.exists():
            return ""
        return hashlib.sha256(p.read_bytes()).hexdigest()

    def snapshot(self, paths: list[str]) -> dict[str, str]:
        """Take hash snapshot of protected files."""
        self._hashes = {p: self.compute_hash(p) for p in paths if Path(p).exists()}
        return dict(self._hashes)

    def verify_integrity(self) -> list[str]:
        """Check if any protected files have been modified since snapshot."""
        violations = []
        for path, expected_hash in self._hashes.items():
            current = self.compute_hash(path)
            if current != expected_hash:
                violations.append(path)
        return violations
