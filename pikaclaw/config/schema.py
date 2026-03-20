"""PikaClaw configuration schema — Pydantic models."""
from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Literal


class ProviderConfig(BaseModel):
    api_key: str = ""
    base_url: str = ""


class SecurityConfig(BaseModel):
    sandbox_enabled: bool = True
    prompt_guard_enabled: bool = True
    audit_logging: bool = True
    sentinel_enabled: bool = True
    max_tool_calls_per_minute: int = 50
    max_bash_per_minute: int = 10
    denied_commands: list[str] = Field(default_factory=lambda: [
        "rm -rf /", "rm -rf /*", "chmod 777", "chmod -R 777",
        "mkfs", "> /dev/sda", "dd if=", ":(){ :|:& };:",
    ])
    protected_paths: list[str] = Field(default_factory=lambda: [
        "pikaclaw/security/*", ".pikaclaw/audit.log",
    ])


class LocalBrainConfig(BaseModel):
    enabled: bool = True
    ollama_url: str = "http://localhost:11434"
    default_model: str = "qwen2.5-coder:3b"
    vram_budget_mb: int = 11000


class WindowConfig(BaseModel):
    width: int = 1200
    height: int = 800
    theme: str = "dark"


class DarwinConfig(BaseModel):
    enabled: bool = False
    schedule: str = "0 3 * * *"
    auto_approve_low_risk: bool = False


class PikaClawConfig(BaseModel):
    default_model: str = "ollama/qwen2.5-coder:3b"
    routing: Literal["balanced", "cheapest", "fastest", "best_quality", "local_only"] = "balanced"
    default_agent: str = "build"
    providers: dict[str, ProviderConfig] = Field(default_factory=dict)
    security: SecurityConfig = Field(default_factory=SecurityConfig)
    local_brain: LocalBrainConfig = Field(default_factory=LocalBrainConfig)
    window: WindowConfig = Field(default_factory=WindowConfig)
    darwin: DarwinConfig = Field(default_factory=DarwinConfig)
    agents: dict[str, dict] = Field(default_factory=dict)
