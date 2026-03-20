"""Ollama local model provider."""
from __future__ import annotations

import json

import httpx


class OllamaProvider:
    """Provider for local Ollama models."""

    def __init__(self, base_url: str = "http://localhost:11434") -> None:
        self.base_url = base_url.rstrip("/")
        self.client = httpx.AsyncClient(base_url=self.base_url, timeout=120.0)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def complete(
        self,
        messages: list[dict],
        model: str,
        tools: list[dict] | None = None,
        stream: bool = False,
    ) -> dict:
        """Send a chat completion request to Ollama and return a standardised result."""
        payload: dict = {
            "model": model,
            "messages": messages,
            "stream": stream,
        }
        if tools:
            payload["tools"] = self._convert_tools(tools)

        try:
            resp = await self.client.post("/api/chat", json=payload)
            resp.raise_for_status()
            data = resp.json()
        except httpx.HTTPStatusError as exc:
            return self._error_response(
                f"Ollama HTTP {exc.response.status_code}: {exc.response.text}"
            )
        except httpx.ConnectError:
            return self._error_response(
                f"Cannot connect to Ollama at {self.base_url}. Is it running?"
            )
        except Exception as exc:  # noqa: BLE001
            return self._error_response(f"Ollama error: {exc}")

        message = data.get("message", {})
        content = message.get("content", "")
        tool_calls = self._parse_tool_calls(message.get("tool_calls"))

        # Ollama exposes token counts at the top level of the response.
        usage = {
            "input_tokens": data.get("prompt_eval_count", 0) or 0,
            "output_tokens": data.get("eval_count", 0) or 0,
        }

        return {"content": content, "tool_calls": tool_calls, "usage": usage}

    async def health_check(self) -> bool:
        """Return *True* if the Ollama server is reachable."""
        try:
            resp = await self.client.get("/")
            return resp.status_code == 200
        except Exception:  # noqa: BLE001
            return False

    async def list_models(self) -> list[str]:
        """Return a list of model names available on the server."""
        try:
            resp = await self.client.get("/api/tags")
            resp.raise_for_status()
            data = resp.json()
            return [m["name"] for m in data.get("models", [])]
        except Exception:  # noqa: BLE001
            return []

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _convert_tools(tools: list[dict]) -> list[dict]:
        """Convert tools to the Ollama (OpenAI-style) function-calling format.

        Accepts either the raw OpenAI format (already wrapped in
        ``{"type": "function", "function": {...}}``) or a flat dict with
        ``name`` / ``description`` / ``parameters`` keys.
        """
        converted: list[dict] = []
        for tool in tools:
            if "type" in tool and tool["type"] == "function" and "function" in tool:
                # Already in OpenAI format — pass through.
                converted.append(tool)
            else:
                converted.append(
                    {
                        "type": "function",
                        "function": {
                            "name": tool.get("name", ""),
                            "description": tool.get("description", ""),
                            "parameters": tool.get("parameters", {}),
                        },
                    }
                )
        return converted

    @staticmethod
    def _parse_tool_calls(raw_calls: list | None) -> list[dict]:
        """Parse Ollama tool_calls into the standardised format.

        Each raw call looks like:
        ``{"function": {"name": "...", "arguments": "..." or {...}}}``
        """
        if not raw_calls:
            return []

        parsed: list[dict] = []
        for call in raw_calls:
            func = call.get("function", {})
            arguments = func.get("arguments", {})
            # arguments may already be a dict or may be a JSON string.
            if isinstance(arguments, str):
                try:
                    arguments = json.loads(arguments)
                except json.JSONDecodeError:
                    arguments = {"raw": arguments}
            parsed.append({"name": func.get("name", ""), "arguments": arguments})
        return parsed

    @staticmethod
    def _error_response(msg: str) -> dict:
        return {
            "content": msg,
            "tool_calls": [],
            "usage": {"input_tokens": 0, "output_tokens": 0},
        }
