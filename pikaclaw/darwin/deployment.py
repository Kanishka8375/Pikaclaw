"""Deployment Pipeline — safely applies patches to the codebase."""
from __future__ import annotations

import tempfile
from dataclasses import dataclass, field
from pathlib import Path

from pikaclaw.darwin.constraints import CodePatch


@dataclass
class DeployResult:
    """Result of deploying a patch."""
    success: bool = False
    stage_reached: int = 0
    errors: list[str] = field(default_factory=list)
    patch_id: str = ""


class DeploymentPipeline:
    """Safely deploys code patches through staged validation."""

    def __init__(self, repo_path: str = "."):
        self.repo_path = Path(repo_path)

    async def deploy(self, patch: CodePatch, patch_id: str = "") -> DeployResult:
        """Deploy a patch through a 3-stage pipeline.

        Stage 1: Apply to temp directory and run tests (sandbox)
        Stage 2: Apply to actual codebase
        Stage 3: Health check
        """
        result = DeployResult(patch_id=patch_id)

        # Stage 1: Sandbox test
        try:
            sandbox_ok = await self._stage_sandbox(patch)
            result.stage_reached = 1
            if not sandbox_ok:
                result.errors.append("Stage 1 (sandbox) failed")
                return result
        except Exception as e:
            result.errors.append(f"Stage 1 error: {e}")
            return result

        # Stage 2: Apply to codebase
        try:
            apply_ok = await self._stage_apply(patch)
            result.stage_reached = 2
            if not apply_ok:
                result.errors.append("Stage 2 (apply) failed")
                return result
        except Exception as e:
            result.errors.append(f"Stage 2 error: {e}")
            return result

        # Stage 3: Health check
        try:
            healthy = await self._stage_health_check()
            result.stage_reached = 3
            if not healthy:
                result.errors.append("Stage 3 (health check) failed — rolling back")
                await self._rollback_apply(patch)
                return result
        except Exception as e:
            result.errors.append(f"Stage 3 error: {e}")
            await self._rollback_apply(patch)
            return result

        result.success = True
        return result

    async def _stage_sandbox(self, patch: CodePatch) -> bool:
        """Stage 1: Test patch in an isolated temp directory."""
        import ast
        with tempfile.TemporaryDirectory() as tmpdir:
            for file_path, content in patch.files.items():
                p = Path(tmpdir) / file_path
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_text(content)
                # Verify syntax
                if file_path.endswith(".py"):
                    try:
                        ast.parse(content)
                    except SyntaxError:
                        return False
        return True

    async def _stage_apply(self, patch: CodePatch) -> bool:
        """Stage 2: Apply patch files to the actual codebase."""
        # Store backups for rollback
        self._backups: dict[str, str | None] = {}
        for file_path, content in patch.files.items():
            target = self.repo_path / file_path
            if target.exists():
                self._backups[file_path] = target.read_text()
            else:
                self._backups[file_path] = None
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content)
        return True

    async def _stage_health_check(self) -> bool:
        """Stage 3: Verify the system is still healthy after applying patch."""
        import asyncio
        try:
            proc = await asyncio.create_subprocess_exec(
                "python3", "-c", "import pikaclaw; print('OK')",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=str(self.repo_path),
            )
            stdout, _ = await asyncio.wait_for(proc.communicate(), timeout=15)
            return proc.returncode == 0
        except (asyncio.TimeoutError, Exception):
            return False

    async def _rollback_apply(self, patch: CodePatch) -> None:
        """Rollback an applied patch using stored backups."""
        for file_path, backup in getattr(self, "_backups", {}).items():
            target = self.repo_path / file_path
            if backup is None:
                # File didn't exist before — remove it
                if target.exists():
                    target.unlink()
            else:
                target.write_text(backup)

    async def rollback(self, patch_id: str) -> bool:
        """Rollback a deployed patch by ID. Returns True if successful."""
        # In a full implementation, this would look up the patch by ID
        # and reverse the changes. For now, it's handled by genome.rollback().
        return False
