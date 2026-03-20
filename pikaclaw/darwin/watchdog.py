"""Darwin Watchdog — integrity monitoring for protected files."""
from __future__ import annotations

import hashlib
import asyncio
import json
from pathlib import Path
from datetime import datetime


class DarwinWatchdog:
    """Monitors protected files for unauthorized modifications."""

    def __init__(self, protected_files: list[str] | None = None):
        self.protected_files = protected_files or [
            "pikaclaw/security/sentinel.py",
            "pikaclaw/security/permissions.py",
            "pikaclaw/security/secrets.py",
            "pikaclaw/darwin/constraints.py",
            "pikaclaw/darwin/watchdog.py",
        ]
        self._manifest: dict[str, str] = {}
        self._manifest_path = Path.home() / ".pikaclaw" / "darwin" / "watchdog_manifest.json"
        self._manifest_path.parent.mkdir(parents=True, exist_ok=True)
        self._task: asyncio.Task | None = None

    def _hash_file(self, path: str) -> str:
        """Compute SHA-256 hash of a file."""
        p = Path(path)
        if not p.exists():
            return "MISSING"
        return hashlib.sha256(p.read_bytes()).hexdigest()

    def snapshot(self) -> dict[str, str]:
        """Take a snapshot of all protected file hashes."""
        self._manifest = {f: self._hash_file(f) for f in self.protected_files}
        # Persist manifest
        self._manifest_path.write_text(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "hashes": self._manifest,
        }, indent=2))
        return dict(self._manifest)

    def verify_integrity(self) -> tuple[bool, list[str]]:
        """Verify all protected files against stored hashes. Returns (ok, violations)."""
        if not self._manifest:
            # Try loading from disk
            if self._manifest_path.exists():
                data = json.loads(self._manifest_path.read_text())
                self._manifest = data.get("hashes", {})
            else:
                # No baseline — take one now
                self.snapshot()
                return True, []

        violations: list[str] = []
        for file_path, expected_hash in self._manifest.items():
            current_hash = self._hash_file(file_path)
            if current_hash != expected_hash:
                violations.append(f"{file_path}: expected {expected_hash[:12]}... got {current_hash[:12]}...")

        return len(violations) == 0, violations

    async def start(self, interval: int = 60) -> None:
        """Start periodic integrity checking."""
        self.snapshot()

        async def _monitor():
            while True:
                await asyncio.sleep(interval)
                ok, violations = self.verify_integrity()
                if not ok:
                    for v in violations:
                        # In production, this would trigger alerts
                        pass

        self._task = asyncio.create_task(_monitor())

    async def stop(self) -> None:
        """Stop periodic integrity checking."""
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            self._task = None
