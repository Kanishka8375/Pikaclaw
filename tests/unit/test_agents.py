"""Tests for the PikaClaw agent registry and definitions."""
from __future__ import annotations

import dataclasses

import pytest

from pikaclaw.agents.base import AgentDefinition
from pikaclaw.agents.registry import AGENTS


# ---------------------------------------------------------------------------
# Registry size and membership
# ---------------------------------------------------------------------------

class TestAgentRegistry:
    def test_agents_has_exactly_9(self):
        assert len(AGENTS) == 9

    @pytest.mark.parametrize(
        "name",
        ["build", "plan", "review", "debug", "test", "security", "research", "darwin", "compact"],
    )
    def test_agent_present(self, name):
        assert name in AGENTS

    def test_all_agents_are_agent_definitions(self):
        for name, agent in AGENTS.items():
            assert isinstance(agent, AgentDefinition), f"{name} is not AgentDefinition"

    def test_all_agents_have_non_empty_system_prompt(self):
        for name, agent in AGENTS.items():
            assert len(agent.system_prompt) > 0, f"{name} has empty system_prompt"

    def test_all_agents_have_icon(self):
        for name, agent in AGENTS.items():
            assert agent.icon, f"{name} has no icon"

    def test_all_agents_have_name_matching_key(self):
        for name, agent in AGENTS.items():
            assert agent.name == name

    def test_all_agents_have_display_name(self):
        for name, agent in AGENTS.items():
            assert agent.display_name, f"{name} has no display_name"

    def test_all_agents_have_description(self):
        for name, agent in AGENTS.items():
            assert agent.description, f"{name} has no description"


# ---------------------------------------------------------------------------
# Primary agents
# ---------------------------------------------------------------------------

class TestPrimaryAgents:
    @pytest.mark.parametrize("name", ["build", "plan", "review", "debug"])
    def test_is_primary(self, name):
        assert AGENTS[name].mode == "primary"


# ---------------------------------------------------------------------------
# Specialist agents
# ---------------------------------------------------------------------------

class TestSpecialistAgents:
    @pytest.mark.parametrize("name", ["test", "security", "research"])
    def test_is_specialist(self, name):
        assert AGENTS[name].mode == "specialist"


# ---------------------------------------------------------------------------
# System agents
# ---------------------------------------------------------------------------

class TestSystemAgents:
    @pytest.mark.parametrize("name", ["darwin", "compact"])
    def test_is_system(self, name):
        assert AGENTS[name].mode == "system"


# ---------------------------------------------------------------------------
# Build agent
# ---------------------------------------------------------------------------

class TestBuildAgent:
    def test_can_write_files(self):
        assert AGENTS["build"].can_write_files is True

    def test_can_execute_bash(self):
        assert AGENTS["build"].can_execute_bash is True

    def test_can_spawn_agents(self):
        assert AGENTS["build"].can_spawn_agents is True

    def test_icon(self):
        assert AGENTS["build"].icon == "\u26a1"


# ---------------------------------------------------------------------------
# Plan agent
# ---------------------------------------------------------------------------

class TestPlanAgent:
    def test_can_write_files_false(self):
        assert AGENTS["plan"].can_write_files is False

    def test_can_execute_bash_false(self):
        assert AGENTS["plan"].can_execute_bash is False

    def test_denied_tools_includes_write(self):
        assert "Write" in AGENTS["plan"].denied_tools

    def test_denied_tools_includes_edit(self):
        assert "Edit" in AGENTS["plan"].denied_tools

    def test_denied_tools_includes_bash(self):
        assert "Bash" in AGENTS["plan"].denied_tools

    def test_denied_tools_includes_git(self):
        assert "Git" in AGENTS["plan"].denied_tools

    def test_can_spawn_agents_false(self):
        assert AGENTS["plan"].can_spawn_agents is False

    def test_preferred_model(self):
        assert AGENTS["plan"].preferred_model == "claude-opus-4-6"


# ---------------------------------------------------------------------------
# Review agent
# ---------------------------------------------------------------------------

class TestReviewAgent:
    def test_can_write_files_false(self):
        assert AGENTS["review"].can_write_files is False

    def test_denied_tools_includes_write(self):
        assert "Write" in AGENTS["review"].denied_tools

    def test_denied_tools_includes_edit(self):
        assert "Edit" in AGENTS["review"].denied_tools

    def test_can_spawn_agents_false(self):
        assert AGENTS["review"].can_spawn_agents is False

    def test_preferred_model(self):
        assert AGENTS["review"].preferred_model == "zhipu/glm-5"


# ---------------------------------------------------------------------------
# Debug agent
# ---------------------------------------------------------------------------

class TestDebugAgent:
    def test_can_write_files(self):
        assert AGENTS["debug"].can_write_files is True

    def test_can_execute_bash(self):
        assert AGENTS["debug"].can_execute_bash is True

    def test_mode(self):
        assert AGENTS["debug"].mode == "primary"


# ---------------------------------------------------------------------------
# Test agent
# ---------------------------------------------------------------------------

class TestTestAgent:
    def test_can_spawn_agents_false(self):
        assert AGENTS["test"].can_spawn_agents is False

    def test_can_write_files(self):
        assert AGENTS["test"].can_write_files is True

    def test_can_execute_bash(self):
        assert AGENTS["test"].can_execute_bash is True

    def test_preferred_model(self):
        assert AGENTS["test"].preferred_model == "minimax/minimax-m2.5"


# ---------------------------------------------------------------------------
# Security agent
# ---------------------------------------------------------------------------

class TestSecurityAgent:
    def test_can_write_files_false(self):
        assert AGENTS["security"].can_write_files is False

    def test_can_spawn_agents_false(self):
        assert AGENTS["security"].can_spawn_agents is False

    def test_denied_tools_includes_write(self):
        assert "Write" in AGENTS["security"].denied_tools

    def test_denied_tools_includes_edit(self):
        assert "Edit" in AGENTS["security"].denied_tools

    def test_preferred_model(self):
        assert AGENTS["security"].preferred_model == "zhipu/glm-5"


# ---------------------------------------------------------------------------
# Research agent
# ---------------------------------------------------------------------------

class TestResearchAgent:
    def test_can_write_files_false(self):
        assert AGENTS["research"].can_write_files is False

    def test_can_execute_bash_false(self):
        assert AGENTS["research"].can_execute_bash is False

    def test_can_spawn_agents_false(self):
        assert AGENTS["research"].can_spawn_agents is False

    def test_denied_tools_includes_write(self):
        assert "Write" in AGENTS["research"].denied_tools

    def test_denied_tools_includes_bash(self):
        assert "Bash" in AGENTS["research"].denied_tools

    def test_denied_tools_includes_git(self):
        assert "Git" in AGENTS["research"].denied_tools

    def test_preferred_model(self):
        assert AGENTS["research"].preferred_model == "minimax/minimax-m2.5"


# ---------------------------------------------------------------------------
# Darwin agent
# ---------------------------------------------------------------------------

class TestDarwinAgent:
    def test_mode_is_system(self):
        assert AGENTS["darwin"].mode == "system"

    def test_can_write_files(self):
        assert AGENTS["darwin"].can_write_files is True

    def test_can_execute_bash(self):
        assert AGENTS["darwin"].can_execute_bash is True

    def test_can_spawn_agents(self):
        assert AGENTS["darwin"].can_spawn_agents is True

    def test_max_turns(self):
        assert AGENTS["darwin"].max_turns == 50


# ---------------------------------------------------------------------------
# Compact agent
# ---------------------------------------------------------------------------

class TestCompactAgent:
    def test_max_turns_one(self):
        assert AGENTS["compact"].max_turns == 1

    def test_can_write_files_false(self):
        assert AGENTS["compact"].can_write_files is False

    def test_can_execute_bash_false(self):
        assert AGENTS["compact"].can_execute_bash is False

    def test_can_spawn_agents_false(self):
        assert AGENTS["compact"].can_spawn_agents is False

    def test_denied_tools_extensive(self):
        denied = AGENTS["compact"].denied_tools
        for tool in ["Write", "Edit", "Bash", "Git", "WebSearch", "WebFetch"]:
            assert tool in denied, f"{tool} not in compact denied_tools"

    def test_preferred_local(self):
        assert AGENTS["compact"].preferred_local == "phi-4-mini"


# ---------------------------------------------------------------------------
# AgentDefinition dataclass
# ---------------------------------------------------------------------------

class TestAgentDefinitionDataclass:
    def test_is_dataclass(self):
        assert dataclasses.is_dataclass(AgentDefinition)

    def test_default_preferred_model_none(self):
        ad = AgentDefinition(
            name="x", display_name="X", description="d", icon="i",
            mode="primary", system_prompt="sp",
        )
        assert ad.preferred_model is None

    def test_default_preferred_local_none(self):
        ad = AgentDefinition(
            name="x", display_name="X", description="d", icon="i",
            mode="primary", system_prompt="sp",
        )
        assert ad.preferred_local is None

    def test_default_temperature(self):
        ad = AgentDefinition(
            name="x", display_name="X", description="d", icon="i",
            mode="primary", system_prompt="sp",
        )
        assert ad.temperature == 0.0

    def test_default_max_turns(self):
        ad = AgentDefinition(
            name="x", display_name="X", description="d", icon="i",
            mode="primary", system_prompt="sp",
        )
        assert ad.max_turns == 250

    def test_default_allowed_tools_empty(self):
        ad = AgentDefinition(
            name="x", display_name="X", description="d", icon="i",
            mode="primary", system_prompt="sp",
        )
        assert ad.allowed_tools == []

    def test_default_denied_tools_empty(self):
        ad = AgentDefinition(
            name="x", display_name="X", description="d", icon="i",
            mode="primary", system_prompt="sp",
        )
        assert ad.denied_tools == []

    def test_default_can_write_files_true(self):
        ad = AgentDefinition(
            name="x", display_name="X", description="d", icon="i",
            mode="primary", system_prompt="sp",
        )
        assert ad.can_write_files is True

    def test_default_can_execute_bash_true(self):
        ad = AgentDefinition(
            name="x", display_name="X", description="d", icon="i",
            mode="primary", system_prompt="sp",
        )
        assert ad.can_execute_bash is True

    def test_default_can_access_network_true(self):
        ad = AgentDefinition(
            name="x", display_name="X", description="d", icon="i",
            mode="primary", system_prompt="sp",
        )
        assert ad.can_access_network is True

    def test_default_can_modify_git_true(self):
        ad = AgentDefinition(
            name="x", display_name="X", description="d", icon="i",
            mode="primary", system_prompt="sp",
        )
        assert ad.can_modify_git is True

    def test_default_can_spawn_agents_true(self):
        ad = AgentDefinition(
            name="x", display_name="X", description="d", icon="i",
            mode="primary", system_prompt="sp",
        )
        assert ad.can_spawn_agents is True

    def test_default_skills_empty(self):
        ad = AgentDefinition(
            name="x", display_name="X", description="d", icon="i",
            mode="primary", system_prompt="sp",
        )
        assert ad.skills == []

    def test_default_auto_load_context_true(self):
        ad = AgentDefinition(
            name="x", display_name="X", description="d", icon="i",
            mode="primary", system_prompt="sp",
        )
        assert ad.auto_load_context is True
