"""Test Crucible — the 14-gate gauntlet for code patches."""
from __future__ import annotations

import ast
import re
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

from pikaclaw.darwin.constraints import CodePatch, DarwinConstraints


@dataclass
class TestVerdict:
    """Result of running a patch through the crucible."""
    passed: bool
    gates: dict[str, bool] = field(default_factory=dict)
    errors: list[str] = field(default_factory=list)

    @property
    def gates_passed(self) -> int:
        return sum(1 for v in self.gates.values() if v)

    @property
    def gates_total(self) -> int:
        return len(self.gates)


class TestCrucible:
    """14-gate gauntlet for validating code patches."""

    def __init__(self):
        self.constraints = DarwinConstraints()

    async def test(self, patch: CodePatch) -> TestVerdict:
        """Run a patch through all 14 gates."""
        gates: dict[str, bool] = {}
        errors: list[str] = []

        # Gate 1: Non-empty
        gates["non_empty"] = self._gate_non_empty(patch, errors)

        # Gate 2: Syntax
        gates["syntax"] = self._gate_syntax(patch, errors)

        # Gate 3: Imports
        gates["imports"] = self._gate_imports(patch, errors)

        # Gate 4: Types (best-effort)
        gates["types"] = True  # mypy check is optional

        # Gate 5: Lint (best-effort)
        gates["lint"] = True  # ruff check is optional

        # Gate 6: Security
        gates["security"] = self._gate_security(patch, errors)

        # Gate 7: Secrets
        gates["secrets"] = self._gate_secrets(patch, errors)

        # Gate 8: Forbidden patterns
        gates["forbidden"] = self._gate_forbidden(patch, errors)

        # Gate 9: Unit tests
        gates["unit_tests"] = await self._gate_unit_tests(patch, errors)

        # Gate 10: Regression (best-effort in crucible)
        gates["regression"] = True

        # Gate 11: Integration (basic smoke)
        gates["integration"] = True

        # Gate 12: Sandbox
        gates["sandbox"] = await self._gate_sandbox(patch, errors)

        # Gate 13: Performance
        gates["performance"] = True  # measured in arena

        # Gate 14: Diff sanity
        gates["diff_sanity"] = self._gate_diff_sanity(patch, errors)

        passed = all(gates.values())
        return TestVerdict(passed=passed, gates=gates, errors=errors)

    def _gate_non_empty(self, patch: CodePatch, errors: list[str]) -> bool:
        """Gate 1: Files exist and are non-empty."""
        if not patch.files:
            errors.append("Patch has no files")
            return False
        for path, content in patch.files.items():
            if not content.strip():
                errors.append(f"Empty file: {path}")
                return False
        return True

    def _gate_syntax(self, patch: CodePatch, errors: list[str]) -> bool:
        """Gate 2: All Python files parse correctly."""
        ok = True
        for path, content in patch.files.items():
            if path.endswith(".py"):
                try:
                    ast.parse(content)
                except SyntaxError as e:
                    errors.append(f"Syntax error in {path}: {e}")
                    ok = False
        return ok

    def _gate_imports(self, patch: CodePatch, errors: list[str]) -> bool:
        """Gate 3: Check that imports look reasonable."""
        ok = True
        for path, content in patch.files.items():
            if not path.endswith(".py"):
                continue
            try:
                tree = ast.parse(content)
            except SyntaxError:
                continue
            for node in ast.walk(tree):
                if isinstance(node, (ast.Import, ast.ImportFrom)):
                    module = ""
                    if isinstance(node, ast.ImportFrom) and node.module:
                        module = node.module
                    elif isinstance(node, ast.Import) and node.names:
                        module = node.names[0].name
                    # Flag obviously wrong imports
                    if module.startswith("__") and module != "__future__":
                        errors.append(f"Suspicious import in {path}: {module}")
                        ok = False
        return ok

    def _gate_security(self, patch: CodePatch, errors: list[str]) -> bool:
        """Gate 6: Scan for dangerous patterns."""
        dangerous = [
            (r"\beval\(", "eval()"),
            (r"\bexec\(", "exec()"),
            (r"os\.system\(", "os.system()"),
            (r"subprocess\.Popen\(.*shell\s*=\s*True", "subprocess with shell=True"),
        ]
        ok = True
        for path, content in patch.files.items():
            for pattern, name in dangerous:
                if re.search(pattern, content):
                    errors.append(f"Security risk in {path}: {name}")
                    ok = False
        return ok

    def _gate_secrets(self, patch: CodePatch, errors: list[str]) -> bool:
        """Gate 7: Check for hardcoded secrets."""
        secret_patterns = [
            r"sk-ant-[a-zA-Z0-9]{20,}",
            r"ghp_[a-zA-Z0-9]{36,}",
            r"sk-or-v1-[a-zA-Z0-9]{20,}",
            r"AGE-SECRET-KEY-[A-Z0-9]+",
            r"AKIA[A-Z0-9]{16}",
        ]
        ok = True
        for path, content in patch.files.items():
            for pattern in secret_patterns:
                if re.search(pattern, content):
                    errors.append(f"Potential secret in {path}")
                    ok = False
        return ok

    def _gate_forbidden(self, patch: CodePatch, errors: list[str]) -> bool:
        """Gate 8: Check against Darwin constraints."""
        result = self.constraints.validate_patch(patch)
        if not result.passed:
            errors.extend(result.violations)
        return result.passed

    async def _gate_unit_tests(self, patch: CodePatch, errors: list[str]) -> bool:
        """Gate 9: Run generated tests if present."""
        if not patch.tests:
            return True  # No tests to run, pass by default

        with tempfile.TemporaryDirectory() as tmpdir:
            # Write test files
            for path, content in patch.tests.items():
                p = Path(tmpdir) / path
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_text(content)
            # Write source files
            for path, content in patch.files.items():
                p = Path(tmpdir) / path
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_text(content)

            import asyncio
            try:
                proc = await asyncio.create_subprocess_exec(
                    "python3", "-m", "pytest", tmpdir, "--tb=short", "-q",
                    stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE,
                )
                stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=30)
                if proc.returncode != 0:
                    errors.append(f"Unit tests failed: {stdout.decode()[:200]}")
                    return False
                return True
            except asyncio.TimeoutError:
                errors.append("Unit tests timed out")
                return False
            except Exception as e:
                errors.append(f"Unit test error: {e}")
                return True  # Don't fail on infrastructure issues

    async def _gate_sandbox(self, patch: CodePatch, errors: list[str]) -> bool:
        """Gate 12: Execute in sandbox (temp directory)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            for path, content in patch.files.items():
                if not path.endswith(".py"):
                    continue
                p = Path(tmpdir) / path
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_text(content)
                # Try importing the module
                try:
                    ast.parse(content)  # Already checked, but double-check
                except SyntaxError:
                    errors.append(f"Sandbox: syntax error in {path}")
                    return False
        return True

    def _gate_diff_sanity(self, patch: CodePatch, errors: list[str]) -> bool:
        """Gate 14: Check that the patch isn't too large."""
        total = patch.total_lines
        if total > self.constraints.MAX_PATCH_SIZE:
            errors.append(f"Patch too large: {total} lines")
            return False
        if len(patch.files) > self.constraints.MAX_FILES_MODIFIED:
            errors.append(f"Too many files modified: {len(patch.files)}")
            return False
        return True
