"""Audit logger with hash chain integrity."""
from __future__ import annotations
import json
import hashlib
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4


class AuditLogger:
    """Append-only audit log with hash chain."""

    def __init__(self, log_dir: str | None = None):
        if log_dir:
            self.log_dir = Path(log_dir)
        else:
            self.log_dir = Path.home() / ".pikaclaw" / "logs"
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.log_file = self.log_dir / "audit.jsonl"
        self.prev_hash = self._get_last_hash()

    def _get_last_hash(self) -> str:
        """Read the hash from the last log entry."""
        if not self.log_file.exists():
            return ""
        try:
            lines = self.log_file.read_text().strip().split("\n")
            if lines and lines[-1]:
                last = json.loads(lines[-1])
                return last.get("hash", "")
        except Exception:
            pass
        return ""

    def log_event(self, action: str, resource: str, result: str, **extra) -> dict:
        """Log an event with hash chain integrity."""
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "id": str(uuid4()),
            "action": action,
            "resource": resource,
            "result": result,
            "prev_hash": self.prev_hash,
        }
        entry.update(extra)

        # Compute hash
        hash_input = json.dumps(entry, sort_keys=True)
        entry["hash"] = hashlib.sha256(hash_input.encode()).hexdigest()
        self.prev_hash = entry["hash"]

        # Append to log
        with open(self.log_file, "a") as f:
            f.write(json.dumps(entry) + "\n")

        return entry

    def verify_chain(self) -> bool:
        """Verify the entire hash chain is intact."""
        if not self.log_file.exists():
            return True
        prev = ""
        for line in self.log_file.read_text().strip().split("\n"):
            if not line:
                continue
            entry = json.loads(line)
            if entry.get("prev_hash", "") != prev:
                return False
            stored_hash = entry.pop("hash")
            computed = hashlib.sha256(json.dumps(entry, sort_keys=True).encode()).hexdigest()
            if computed != stored_hash:
                return False
            prev = stored_hash
            entry["hash"] = stored_hash
        return True
