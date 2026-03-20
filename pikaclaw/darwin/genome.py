"""Evolution Genome — tracks and commits evolution patches."""
from __future__ import annotations

import asyncio
import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

from pikaclaw.darwin.constraints import CodePatch
from pikaclaw.darwin.lab import Hypothesis


@dataclass
class EvolutionEntry:
    """A record of an evolution commit."""
    commit_hash: str = ""
    branch: str = ""
    timestamp: str = ""
    hypothesis: str = ""
    technique: str = ""
    files_changed: int = 0


class EvolutionGenome:
    """Manages the evolutionary history of PikaClaw."""

    def __init__(self, repo_path: str = "."):
        self.repo_path = Path(repo_path)
        self._log_path = Path.home() / ".pikaclaw" / "darwin" / "genome_log.json"
        self._log_path.parent.mkdir(parents=True, exist_ok=True)
        self._generation = 0
        self._load_log()

    def _load_log(self):
        """Load evolution log from disk."""
        if self._log_path.exists():
            try:
                data = json.loads(self._log_path.read_text())
                self._generation = data.get("generation", 0)
            except (json.JSONDecodeError, KeyError):
                self._generation = 0

    def _save_log(self, entries: list[dict]):
        """Save evolution log to disk."""
        self._log_path.write_text(json.dumps({
            "generation": self._generation,
            "entries": entries,
        }, indent=2))

    def get_generation(self) -> int:
        """Get the current evolution generation count."""
        return self._generation

    async def commit(self, patch: CodePatch, hypothesis: Hypothesis) -> str:
        """Write patch files and record the commit (without actually git-committing).

        Returns a pseudo-commit hash for tracking.
        """
        import hashlib

        # Generate a stable hash for this patch
        content_hash = hashlib.sha256(
            json.dumps(sorted(patch.files.items())).encode()
        ).hexdigest()[:12]

        timestamp = datetime.utcnow().isoformat()
        branch_name = f"darwin/{hypothesis.technique}-{timestamp[:10]}-{content_hash[:6]}"

        entry = EvolutionEntry(
            commit_hash=content_hash,
            branch=branch_name,
            timestamp=timestamp,
            hypothesis=hypothesis.description,
            technique=hypothesis.technique,
            files_changed=len(patch.files),
        )

        # Load existing entries
        existing: list[dict] = []
        if self._log_path.exists():
            try:
                data = json.loads(self._log_path.read_text())
                existing = data.get("entries", [])
            except (json.JSONDecodeError, KeyError):
                pass

        existing.append({
            "commit_hash": entry.commit_hash,
            "branch": entry.branch,
            "timestamp": entry.timestamp,
            "hypothesis": entry.hypothesis,
            "technique": entry.technique,
            "files_changed": entry.files_changed,
        })

        self._generation += 1
        self._save_log(existing)

        return content_hash

    async def rollback(self, commit_hash: str) -> bool:
        """Remove a commit from the evolution log."""
        if not self._log_path.exists():
            return False
        try:
            data = json.loads(self._log_path.read_text())
            entries = data.get("entries", [])
            new_entries = [e for e in entries if e.get("commit_hash") != commit_hash]
            if len(new_entries) == len(entries):
                return False  # Not found
            self._save_log(new_entries)
            return True
        except (json.JSONDecodeError, KeyError):
            return False

    def get_evolution_log(self, limit: int = 20) -> list[EvolutionEntry]:
        """Get recent evolution entries."""
        if not self._log_path.exists():
            return []
        try:
            data = json.loads(self._log_path.read_text())
            entries = data.get("entries", [])[-limit:]
            return [
                EvolutionEntry(
                    commit_hash=e.get("commit_hash", ""),
                    branch=e.get("branch", ""),
                    timestamp=e.get("timestamp", ""),
                    hypothesis=e.get("hypothesis", ""),
                    technique=e.get("technique", ""),
                    files_changed=e.get("files_changed", 0),
                )
                for e in entries
            ]
        except (json.JSONDecodeError, KeyError):
            return []
