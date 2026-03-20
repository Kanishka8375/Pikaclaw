"""Load PikaClaw configuration with auto-detection."""
from __future__ import annotations
import json
import os
from pathlib import Path
from pikaclaw.config.schema import PikaClawConfig, ProviderConfig

def _detect_ollama_models(base_url: str = "http://localhost:11434") -> list[str]:
    """Synchronously check Ollama for installed models."""
    try:
        import httpx
        resp = httpx.get(f"{base_url}/api/tags", timeout=3)
        if resp.status_code == 200:
            data = resp.json()
            return [m["name"] for m in data.get("models", [])]
    except Exception:
        pass
    return []


def _load_api_keys() -> dict[str, str]:
    """Load API keys from env vars and keys file."""
    keys = {}
    for env_var, provider in [
        ("ANTHROPIC_API_KEY", "anthropic"),
        ("OPENROUTER_API_KEY", "openrouter"),
    ]:
        val = os.environ.get(env_var, "")
        if val:
            keys[provider] = val

    keys_file = Path.home() / ".pikaclaw" / "keys" / "api_keys.json"
    if keys_file.exists():
        try:
            file_keys = json.loads(keys_file.read_text())
            for k, v in file_keys.items():
                if v and k not in keys:
                    keys[k] = v
        except Exception:
            pass
    return keys


def load_config() -> PikaClawConfig:
    """Load config from CWD/pikaclaw.json -> ~/.pikaclaw/config.json -> defaults.

    Auto-detects Ollama models and sets default_model accordingly.
    """
    data = {}

    # Try CWD first
    cwd_config = Path.cwd() / "pikaclaw.json"
    home_config = Path.home() / ".pikaclaw" / "config.json"

    for path in [cwd_config, home_config]:
        if path.exists():
            try:
                data = json.loads(path.read_text())
                break
            except Exception:
                continue

    config = PikaClawConfig(**data)

    # Auto-detect Ollama models
    ollama_url = config.local_brain.ollama_url
    models = _detect_ollama_models(ollama_url)
    if models:
        # Prefer coder models, then any model
        coder_models = [m for m in models if "coder" in m.lower()]
        best = coder_models[0] if coder_models else models[0]
        config.default_model = f"ollama/{best}"
        config.local_brain.default_model = best

    # Load API keys into providers
    api_keys = _load_api_keys()
    for provider, key in api_keys.items():
        if provider not in config.providers:
            config.providers[provider] = ProviderConfig(api_key=key)
        elif not config.providers[provider].api_key:
            config.providers[provider].api_key = key

    return config
