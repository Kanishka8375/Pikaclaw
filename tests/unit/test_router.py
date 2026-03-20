"""Tests for the PikaClaw model router."""
from __future__ import annotations

import os
from unittest.mock import patch, MagicMock

import pytest

from pikaclaw.config.schema import PikaClawConfig, ProviderConfig
from pikaclaw.models.router import ModelRouter, MODEL_PROFILES


# ---------------------------------------------------------------------------
# MODEL_PROFILES
# ---------------------------------------------------------------------------

class TestModelProfiles:
    def test_model_profiles_is_dict(self):
        assert isinstance(MODEL_PROFILES, dict)

    def test_has_ollama_qwen_7b(self):
        assert "ollama/qwen2.5-coder:7b" in MODEL_PROFILES

    def test_has_ollama_qwen_3b(self):
        assert "ollama/qwen2.5-coder:3b" in MODEL_PROFILES

    def test_has_claude_sonnet(self):
        assert "claude-sonnet-4-6" in MODEL_PROFILES

    def test_has_claude_opus(self):
        assert "claude-opus-4-6" in MODEL_PROFILES

    def test_has_zhipu_glm5(self):
        assert "zhipu/glm-5" in MODEL_PROFILES

    def test_has_minimax(self):
        assert "minimax/minimax-m2.5" in MODEL_PROFILES

    def test_local_models_have_zero_cost(self):
        for key, profile in MODEL_PROFILES.items():
            if profile["tier"] == "local":
                assert profile["cost_input"] == 0
                assert profile["cost_output"] == 0

    def test_cloud_models_have_positive_cost(self):
        for key, profile in MODEL_PROFILES.items():
            if profile["tier"] != "local":
                assert profile["cost_input"] > 0 or profile["cost_output"] > 0

    def test_all_profiles_have_tier(self):
        for key, profile in MODEL_PROFILES.items():
            assert "tier" in profile, f"{key} missing tier"

    def test_all_profiles_have_cost_input(self):
        for key, profile in MODEL_PROFILES.items():
            assert "cost_input" in profile, f"{key} missing cost_input"

    def test_all_profiles_have_cost_output(self):
        for key, profile in MODEL_PROFILES.items():
            assert "cost_output" in profile, f"{key} missing cost_output"

    def test_profile_count(self):
        assert len(MODEL_PROFILES) == 6


# ---------------------------------------------------------------------------
# ModelRouter initialization
# ---------------------------------------------------------------------------

class TestModelRouterInit:
    def test_initializes_with_config(self):
        config = PikaClawConfig()
        router = ModelRouter(config)
        assert router.config is config

    def test_has_providers_dict(self):
        config = PikaClawConfig()
        router = ModelRouter(config)
        assert isinstance(router.providers, dict)

    def test_has_ollama_provider_by_default(self):
        config = PikaClawConfig()
        router = ModelRouter(config)
        assert "ollama" in router.providers

    def test_no_anthropic_without_key(self, monkeypatch):
        monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
        config = PikaClawConfig()
        router = ModelRouter(config)
        assert "anthropic" not in router.providers

    def test_no_openrouter_without_key(self, monkeypatch):
        monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
        config = PikaClawConfig()
        router = ModelRouter(config)
        assert "openrouter" not in router.providers

    def test_adds_anthropic_provider_with_env_var(self, monkeypatch):
        monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-test-key")
        config = PikaClawConfig()
        router = ModelRouter(config)
        assert "anthropic" in router.providers

    def test_adds_openrouter_provider_with_env_var(self, monkeypatch):
        monkeypatch.setenv("OPENROUTER_API_KEY", "sk-or-test-key")
        config = PikaClawConfig()
        router = ModelRouter(config)
        assert "openrouter" in router.providers

    def test_adds_anthropic_from_config_providers(self, monkeypatch):
        monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
        config = PikaClawConfig(
            providers={"anthropic": ProviderConfig(api_key="sk-from-config")}
        )
        router = ModelRouter(config)
        assert "anthropic" in router.providers

    def test_adds_openrouter_from_config_providers(self, monkeypatch):
        monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
        config = PikaClawConfig(
            providers={"openrouter": ProviderConfig(api_key="sk-or-from-config")}
        )
        router = ModelRouter(config)
        assert "openrouter" in router.providers

    def test_env_var_takes_precedence_over_config_for_anthropic(self, monkeypatch):
        monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-env")
        config = PikaClawConfig(
            providers={"anthropic": ProviderConfig(api_key="sk-config")}
        )
        router = ModelRouter(config)
        assert "anthropic" in router.providers
        # The provider should exist regardless of which key wins
        assert router.providers["anthropic"].api_key == "sk-env"


# ---------------------------------------------------------------------------
# _parse_model
# ---------------------------------------------------------------------------

class TestParseModel:
    def _make_router(self, monkeypatch):
        monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
        monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
        config = PikaClawConfig()
        return ModelRouter(config)

    def test_ollama_model_parsed(self, monkeypatch):
        router = self._make_router(monkeypatch)
        provider, model = router._parse_model("ollama/qwen2.5-coder:3b")
        assert provider == "ollama"
        assert model == "qwen2.5-coder:3b"

    def test_claude_sonnet_parsed(self, monkeypatch):
        router = self._make_router(monkeypatch)
        provider, model = router._parse_model("claude-sonnet-4-6")
        assert provider == "anthropic"
        assert model == "claude-sonnet-4-6"

    def test_claude_opus_parsed(self, monkeypatch):
        router = self._make_router(monkeypatch)
        provider, model = router._parse_model("claude-opus-4-6")
        assert provider == "anthropic"
        assert model == "claude-opus-4-6"

    def test_zhipu_glm5_parsed_as_openrouter(self, monkeypatch):
        router = self._make_router(monkeypatch)
        provider, model = router._parse_model("zhipu/glm-5")
        assert provider == "openrouter"
        assert model == "zhipu/glm-5"

    def test_minimax_parsed_as_openrouter(self, monkeypatch):
        router = self._make_router(monkeypatch)
        provider, model = router._parse_model("minimax/minimax-m2.5")
        assert provider == "openrouter"
        assert model == "minimax/minimax-m2.5"

    def test_unknown_prefix_uses_prefix_as_provider(self, monkeypatch):
        router = self._make_router(monkeypatch)
        provider, model = router._parse_model("together/llama-70b")
        assert provider == "together"
        assert model == "llama-70b"

    def test_no_prefix_non_claude_defaults_ollama(self, monkeypatch):
        router = self._make_router(monkeypatch)
        provider, model = router._parse_model("llama3:8b")
        assert provider == "ollama"
        assert model == "llama3:8b"

    def test_no_prefix_claude_defaults_anthropic(self, monkeypatch):
        router = self._make_router(monkeypatch)
        provider, model = router._parse_model("claude-3-haiku")
        assert provider == "anthropic"
        assert model == "claude-3-haiku"

    def test_ollama_with_tag(self, monkeypatch):
        router = self._make_router(monkeypatch)
        provider, model = router._parse_model("ollama/deepseek-coder:6.7b")
        assert provider == "ollama"
        assert model == "deepseek-coder:6.7b"


# ---------------------------------------------------------------------------
# estimate_cost
# ---------------------------------------------------------------------------

class TestEstimateCost:
    def _make_router(self, monkeypatch):
        monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
        monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
        config = PikaClawConfig()
        return ModelRouter(config)

    def test_local_model_zero_cost(self, monkeypatch):
        router = self._make_router(monkeypatch)
        cost = router.estimate_cost("ollama/qwen2.5-coder:3b", 1000, 500)
        assert cost == 0.0

    def test_local_model_7b_zero_cost(self, monkeypatch):
        router = self._make_router(monkeypatch)
        cost = router.estimate_cost("ollama/qwen2.5-coder:7b", 10000, 5000)
        assert cost == 0.0

    def test_claude_sonnet_positive_cost(self, monkeypatch):
        router = self._make_router(monkeypatch)
        cost = router.estimate_cost("claude-sonnet-4-6", 1000, 1000)
        assert cost > 0

    def test_claude_opus_positive_cost(self, monkeypatch):
        router = self._make_router(monkeypatch)
        cost = router.estimate_cost("claude-opus-4-6", 1000, 1000)
        assert cost > 0

    def test_claude_opus_more_expensive_than_sonnet(self, monkeypatch):
        router = self._make_router(monkeypatch)
        opus_cost = router.estimate_cost("claude-opus-4-6", 1000, 1000)
        sonnet_cost = router.estimate_cost("claude-sonnet-4-6", 1000, 1000)
        assert opus_cost > sonnet_cost

    def test_zhipu_positive_cost(self, monkeypatch):
        router = self._make_router(monkeypatch)
        cost = router.estimate_cost("zhipu/glm-5", 1000, 1000)
        assert cost > 0

    def test_minimax_positive_cost(self, monkeypatch):
        router = self._make_router(monkeypatch)
        cost = router.estimate_cost("minimax/minimax-m2.5", 1000, 1000)
        assert cost > 0

    def test_unknown_model_zero_cost(self, monkeypatch):
        router = self._make_router(monkeypatch)
        cost = router.estimate_cost("unknown/model", 1000, 1000)
        assert cost == 0.0

    def test_zero_tokens_zero_cost(self, monkeypatch):
        router = self._make_router(monkeypatch)
        cost = router.estimate_cost("claude-opus-4-6", 0, 0)
        assert cost == 0.0

    def test_cost_scales_with_tokens(self, monkeypatch):
        router = self._make_router(monkeypatch)
        cost_small = router.estimate_cost("claude-sonnet-4-6", 100, 100)
        cost_large = router.estimate_cost("claude-sonnet-4-6", 10000, 10000)
        assert cost_large > cost_small

    def test_cost_calculation_correct_for_sonnet(self, monkeypatch):
        router = self._make_router(monkeypatch)
        # claude-sonnet-4-6: cost_input=3.0, cost_output=15.0 per 1M tokens
        cost = router.estimate_cost("claude-sonnet-4-6", 1_000_000, 1_000_000)
        assert cost == pytest.approx(3.0 + 15.0)

    def test_cost_calculation_correct_for_opus(self, monkeypatch):
        router = self._make_router(monkeypatch)
        # claude-opus-4-6: cost_input=5.0, cost_output=25.0 per 1M tokens
        cost = router.estimate_cost("claude-opus-4-6", 1_000_000, 1_000_000)
        assert cost == pytest.approx(5.0 + 25.0)
