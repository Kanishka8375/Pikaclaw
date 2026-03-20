"""Skill loader — loads .md skill files from .pikaclaw/skills/."""
from __future__ import annotations
from pathlib import Path


class SkillLoader:
    """Discovers and loads skill files."""

    def __init__(self, skills_dir: str | None = None):
        self.skills_dir = Path(skills_dir) if skills_dir else Path.home() / ".pikaclaw" / "skills"
        self._skills: dict[str, dict] = {}

    def load_all(self) -> dict[str, dict]:
        """Load all .md skill files."""
        if not self.skills_dir.exists():
            return {}
        for f in self.skills_dir.glob("*.md"):
            try:
                content = f.read_text()
                name = f.stem
                # Parse simple YAML frontmatter
                meta = {"name": name, "description": "", "auto_load": False}
                if content.startswith("---"):
                    parts = content.split("---", 2)
                    if len(parts) >= 3:
                        for line in parts[1].strip().split("\n"):
                            if ":" in line:
                                k, v = line.split(":", 1)
                                meta[k.strip()] = v.strip()
                        content = parts[2].strip()
                self._skills[name] = {"meta": meta, "content": content}
            except Exception:
                continue
        return self._skills

    def get_skill(self, name: str) -> str | None:
        if name in self._skills:
            return self._skills[name]["content"]
        return None
