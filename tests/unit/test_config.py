"""Tests for the PikaClaw configuration system."""
from __future__ import annotations

import json
import os
from pathlib import Path
from unittest.mock import patch

import pytest

from pikaclaw.config.schema import (
    DarwinConfig,
    LocalBrainConfig,
    PikaClawConfig,
    ProviderConfig,
    SecurityConfig,
    WindowConfig,
)
from pikaclaw.config.loader import load_config


# ---------------------------------------------------------------------------
# PikaClawConfig defaults
# ---------------------------------------------------------------------------

class TestPikaClawConfigDefaults:
    def test_load_config_returns_pikaclaw_config_instance(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
        monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
        with patch("pikaclaw.config.loader._detect_ollama_models", return_value=[]):
            config = load_config()
        assert isinstance(config, PikaClawConfig)

    def test_default_model(self):
        config = PikaClawConfig()
        assert config.default_model == "ollama/qwen2.5-coder:3b"

    def test_default_routing(self):
        config = PikaClawConfig()
        assert config.routing == "balanced"

    def test_default_agent(self):
        config = PikaClawConfig()
        assert config.default_agent == "build"

    def test_default_providers_empty(self):
        config = PikaClawConfig()
        assert config.providers == {}

    def test_default_agents_empty(self):
        config = PikaClawConfig()
        assert config.agents == {}

    def test_attribute_access_default_model(self):
        config = PikaClawConfig()
        assert hasattr(config, "default_model")
        assert config.default_model == "ollama/qwen2.5-coder:3b"

    def test_attribute_access_security(self):
        config = PikaClawConfig()
        assert hasattr(config, "security")
        assert isinstance(config.security, SecurityConfig)

    def test_attribute_access_security_sandbox_enabled(self):
        config = PikaClawConfig()
        assert config.security.sandbox_enabled is True

    def test_routing_accepts_valid_literals(self):
        for val in ("balanced", "cheapest", "fastest", "best_quality", "local_only"):
            config = PikaClawConfig(routing=val)
            assert config.routing == val

    def test_routing_rejects_invalid_value(self):
        with pytest.raises(Exception):
            PikaClawConfig(routing="invalid")


# ---------------------------------------------------------------------------
# SecurityConfig defaults
# ---------------------------------------------------------------------------

class TestSecurityConfigDefaults:
    def test_sandbox_enabled_default(self):
        sc = SecurityConfig()
        assert sc.sandbox_enabled is True

    def test_prompt_guard_enabled_default(self):
        sc = SecurityConfig()
        assert sc.prompt_guard_enabled is True

    def test_audit_logging_default(self):
        sc = SecurityConfig()
        assert sc.audit_logging is True

    def test_sentinel_enabled_default(self):
        sc = SecurityConfig()
        assert sc.sentinel_enabled is True

    def test_max_tool_calls_per_minute_default(self):
        sc = SecurityConfig()
        assert sc.max_tool_calls_per_minute == 50

    def test_max_bash_per_minute_default(self):
        sc = SecurityConfig()
        assert sc.max_bash_per_minute == 10

    def test_denied_commands_is_list(self):
        sc = SecurityConfig()
        assert isinstance(sc.denied_commands, list)
        assert len(sc.denied_commands) > 0

    def test_denied_commands_contains_rm_rf(self):
        sc = SecurityConfig()
        assert "rm -rf /" in sc.denied_commands

    def test_protected_paths_is_list(self):
        sc = SecurityConfig()
        assert isinstance(sc.protected_paths, list)
        assert len(sc.protected_paths) > 0


# ---------------------------------------------------------------------------
# ProviderConfig defaults
# ---------------------------------------------------------------------------

class TestProviderConfigDefaults:
    def test_api_key_default_empty(self):
        pc = ProviderConfig()
        assert pc.api_key == ""

    def test_base_url_default_empty(self):
        pc = ProviderConfig()
        assert pc.base_url == ""

    def test_with_values(self):
        pc = ProviderConfig(api_key="sk-test", base_url="https://example.com")
        assert pc.api_key == "sk-test"
        assert pc.base_url == "https://example.com"


# ---------------------------------------------------------------------------
# WindowConfig defaults
# ---------------------------------------------------------------------------

class TestWindowConfigDefaults:
    def test_width_default(self):
        wc = WindowConfig()
        assert wc.width == 1200

    def test_height_default(self):
        wc = WindowConfig()
        assert wc.height == 800

    def test_theme_default(self):
        wc = WindowConfig()
        assert wc.theme == "dark"


# ---------------------------------------------------------------------------
# DarwinConfig defaults
# ---------------------------------------------------------------------------

class TestDarwinConfigDefaults:
    def test_enabled_default(self):
        dc = DarwinConfig()
        assert dc.enabled is False

    def test_schedule_default(self):
        dc = DarwinConfig()
        assert dc.schedule == "0 3 * * *"

    def test_auto_approve_low_risk_default(self):
        dc = DarwinConfig()
        assert dc.auto_approve_low_risk is False


# ---------------------------------------------------------------------------
# LocalBrainConfig defaults
# ---------------------------------------------------------------------------

class TestLocalBrainConfigDefaults:
    def test_enabled_default(self):
        lbc = LocalBrainConfig()
        assert lbc.enabled is True

    def test_ollama_url_default(self):
        lbc = LocalBrainConfig()
        assert lbc.ollama_url == "http://localhost:11434"

    def test_default_model(self):
        lbc = LocalBrainConfig()
        assert lbc.default_model == "qwen2.5-coder:3b"

    def test_vram_budget_mb_default(self):
        lbc = LocalBrainConfig()
        assert lbc.vram_budget_mb == 11000


# ---------------------------------------------------------------------------
# Config loading from file
# ---------------------------------------------------------------------------

class TestConfigLoadFromFile:
    def test_loads_from_pikaclaw_json(self, tmp_path, monkeypatch):
        config_data = {"default_model": "ollama/llama3:8b", "routing": "fastest"}
        (tmp_path / "pikaclaw.json").write_text(json.dumps(config_data))
        monkeypatch.chdir(tmp_path)
        monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
        monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
        with patch("pikaclaw.config.loader._detect_ollama_models", return_value=[]):
            config = load_config()
        assert config.default_model == "ollama/llama3:8b"
        assert config.routing == "fastest"

    def test_missing_file_falls_back_to_defaults(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
        monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
        with patch("pikaclaw.config.loader._detect_ollama_models", return_value=[]):
            config = load_config()
        assert config.default_model == "ollama/qwen2.5-coder:3b"
        assert config.routing == "balanced"

    def test_partial_config_file_merges_with_defaults(self, tmp_path, monkeypatch):
        config_data = {"default_agent": "plan"}
        (tmp_path / "pikaclaw.json").write_text(json.dumps(config_data))
        monkeypatch.chdir(tmp_path)
        monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
        monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
        with patch("pikaclaw.config.loader._detect_ollama_models", return_value=[]):
            config = load_config()
        assert config.default_agent == "plan"
        assert config.default_model == "ollama/qwen2.5-coder:3b"

    def test_invalid_json_falls_back_to_defaults(self, tmp_path, monkeypatch):
        (tmp_path / "pikaclaw.json").write_text("NOT JSON")
        monkeypatch.chdir(tmp_path)
        monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
        monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
        with patch("pikaclaw.config.loader._detect_ollama_models", return_value=[]):
            config = load_config()
        assert config.default_model == "ollama/qwen2.5-coder:3b"

    def test_config_with_security_override(self, tmp_path, monkeypatch):
        config_data = {"security": {"sandbox_enabled": False, "max_bash_per_minute": 20}}
        (tmp_path / "pikaclaw.json").write_text(json.dumps(config_data))
        monkeypatch.chdir(tmp_path)
        monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
        monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
        with patch("pikaclaw.config.loader._detect_ollama_models", return_value=[]):
            config = load_config()
        assert config.security.sandbox_enabled is False
        assert config.security.max_bash_per_minute == 20

    def test_config_with_nested_window(self, tmp_path, monkeypatch):
        config_data = {"window": {"width": 1920, "height": 1080, "theme": "light"}}
        (tmp_path / "pikaclaw.json").write_text(json.dumps(config_data))
        monkeypatch.chdir(tmp_path)
        monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
        monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
        with patch("pikaclaw.config.loader._detect_ollama_models", return_value=[]):
            config = load_config()
        assert config.window.width == 1920
        assert config.window.theme == "light"
