"""Model router — intelligent multi-provider routing."""
from __future__ import annotations

import os
from typing import TYPE_CHECKING

from pikaclaw.models.providers.ollama import OllamaProvider
from pikaclaw.models.providers.anthropic import AnthropicProvider
from pikaclaw.models.providers.openrouter import OpenRouterProvider

if TYPE_CHECKING:
    from pikaclaw.config.schema import PikaClawConfig

MODEL_PROFILES = {
    "ollama/qwen2.5-coder:7b": {"tier": "local", "cost_input": 0, "cost_output": 0},
    "ollama/qwen2.5-coder:3b": {"tier": "local", "cost_input": 0, "cost_output": 0},
    "claude-sonnet-4-6": {"tier": "workhorse", "cost_input": 3.0, "cost_output": 15.0},
    "claude-opus-4-6": {"tier": "frontier", "cost_input": 5.0, "cost_output": 25.0},
    "zhipu/glm-5": {"tier": "workhorse", "cost_input": 0.8, "cost_output": 2.56},
    "minimax/minimax-m2.5": {"tier": "workhorse", "cost_input": 0.3, "cost_output": 1.2},
}


class ModelRouter:
    def __init__(self, config: PikaClawConfig):
        self.config = config
        self.providers: dict[str, object] = {}
        self._init_providers()

    def _init_providers(self):
        self.providers["ollama"] = OllamaProvider(self.config.local_brain.ollama_url)

        anthropic_key = os.environ.get("ANTHROPIC_API_KEY", "")
        if not anthropic_key and "anthropic" in self.config.providers:
            anthropic_key = self.config.providers["anthropic"].api_key
        if anthropic_key:
            self.providers["anthropic"] = AnthropicProvider(anthropic_key)

        or_key = os.environ.get("OPENROUTER_API_KEY", "")
        if not or_key and "openrouter" in self.config.providers:
            or_key = self.config.providers["openrouter"].api_key
        if or_key:
            self.providers["openrouter"] = OpenRouterProvider(or_key)

    def _parse_model(self, model_str: str) -> tuple[str, str]:
        """Parse 'provider/model' -> (provider, model). Handle special cases."""
        if "/" in model_str:
            provider, model = model_str.split("/", 1)
            # Map known provider prefixes
            if provider in ("zhipu", "minimax"):
                return "openrouter", model_str  # full string as model for openrouter
            return provider, model
        # No prefix — guess provider
        if model_str.startswith("claude"):
            return "anthropic", model_str
        return "ollama", model_str

    async def complete(
        self,
        messages: list[dict],
        model: str | None = None,
        tools: list[dict] | None = None,
        system: str | None = None,
    ) -> dict:
        """Route to the right provider and get completion."""
        model = model or self.config.default_model
        provider_name, model_name = self._parse_model(model)

        # Build fallback chain
        fallbacks = [provider_name]
        for p in ["ollama", "openrouter", "anthropic"]:
            if p not in fallbacks and p in self.providers:
                fallbacks.append(p)

        last_error = None
        for pname in fallbacks:
            provider = self.providers.get(pname)
            if not provider:
                continue
            try:
                # For anthropic, pass system separately
                if pname == "anthropic":
                    return await provider.complete(messages, model_name, tools=tools, system=system)
                else:
                    # Inject system message for non-anthropic providers
                    msgs = messages
                    if system:
                        msgs = [{"role": "system", "content": system}] + messages
                    return await provider.complete(msgs, model_name, tools=tools)
            except Exception as e:
                last_error = e
                continue

        return {
            "content": f"Error: No provider available. Last error: {last_error}",
            "tool_calls": [],
            "usage": {"input_tokens": 0, "output_tokens": 0},
        }

    def estimate_cost(self, model: str, input_tokens: int, output_tokens: int) -> float:
        profile = MODEL_PROFILES.get(model, {})
        cost_in = profile.get("cost_input", 0) * input_tokens / 1_000_000
        cost_out = profile.get("cost_output", 0) * output_tokens / 1_000_000
        return cost_in + cost_out
