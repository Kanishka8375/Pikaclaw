"""Code Forge — implements hypotheses as code patches."""
from __future__ import annotations

from pikaclaw.darwin.constraints import CodePatch
from pikaclaw.darwin.lab import Hypothesis


class CodeForge:
    """Generates code patches from hypotheses."""

    def __init__(self, model_router=None):
        self.router = model_router

    def estimate_complexity(self, hypothesis: Hypothesis) -> int:
        """Estimate implementation complexity (1-10)."""
        technique_complexity = {
            "retry_with_backoff": 3,
            "prompt_refinement": 2,
            "model_routing": 5,
            "context_compression": 6,
            "caching": 4,
            "parallel_execution": 7,
        }
        return technique_complexity.get(hypothesis.technique, 5)

    async def implement(self, hypothesis: Hypothesis) -> CodePatch:
        """Implement a hypothesis as a code patch.

        If a model router is available, uses LLM to generate the patch.
        Otherwise, returns a template patch based on the technique.
        """
        technique = hypothesis.technique

        if self.router:
            return await self._implement_with_llm(hypothesis)

        # Template-based implementation (no LLM needed)
        return self._implement_template(hypothesis)

    async def _implement_with_llm(self, hypothesis: Hypothesis) -> CodePatch:
        """Use LLM to generate implementation."""
        prompt = (
            f"Implement the following improvement for PikaClaw:\n"
            f"Technique: {hypothesis.technique}\n"
            f"Mechanism: {hypothesis.mechanism}\n"
            f"Target: {hypothesis.target_weakness}\n\n"
            f"Generate Python code that implements this. "
            f"Return only the code, no explanation."
        )
        try:
            response = await self.router.complete(
                messages=[{"role": "user", "content": prompt}]
            )
            content = response.get("content", "")
            return CodePatch(
                files={f"pikaclaw/improvements/{hypothesis.technique}.py": content},
                metadata={"hypothesis": hypothesis.technique, "llm_generated": True},
            )
        except Exception:
            return self._implement_template(hypothesis)

    def _implement_template(self, hypothesis: Hypothesis) -> CodePatch:
        """Generate a template-based patch."""
        templates = {
            "retry_with_backoff": {
                "pikaclaw/improvements/retry.py": (
                    '"""Retry with exponential backoff."""\n'
                    "import asyncio\n\n"
                    "async def retry_with_backoff(coro_func, max_retries=3, base_delay=1.0):\n"
                    '    """Retry an async function with exponential backoff."""\n'
                    "    for attempt in range(max_retries):\n"
                    "        try:\n"
                    "            return await coro_func()\n"
                    "        except Exception as e:\n"
                    "            if attempt == max_retries - 1:\n"
                    "                raise\n"
                    "            delay = base_delay * (2 ** attempt)\n"
                    "            await asyncio.sleep(delay)\n"
                ),
            },
            "prompt_refinement": {
                "pikaclaw/improvements/prompts.py": (
                    '"""Refined system prompts."""\n\n'
                    "REFINED_PROMPTS = {\n"
                    '    "build": "You are a precise coding assistant. Always verify your work before responding.",\n'
                    '    "debug": "You are a systematic debugger. Always reproduce the issue first.",\n'
                    "}\n"
                ),
            },
        }

        files = templates.get(hypothesis.technique, {
            f"pikaclaw/improvements/{hypothesis.technique}.py": (
                f'"""Auto-generated improvement: {hypothesis.technique}."""\n'
                f"# Technique: {hypothesis.technique}\n"
                f"# Mechanism: {hypothesis.mechanism}\n"
                f"# Target: {hypothesis.target_weakness}\n\n"
                f"# TODO: Implement {hypothesis.technique}\n"
            ),
        })

        return CodePatch(
            files=files,
            metadata={"hypothesis": hypothesis.technique, "llm_generated": False},
        )
