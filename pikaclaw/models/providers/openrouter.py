"""OpenRouter API provider (OpenAI-compatible)."""
from __future__ import annotations

import json

import httpx


class OpenRouterProvider:
    """Provider for the OpenRouter chat completions API."""

    def __init__(self, api_key: str) -> None:
        self.api_key = api_key
        self.client = httpx.AsyncClient(
            base_url="https://openrouter.ai/api/v1",
            headers={
                "Authorization": f"Bearer {api_key}",
                "content-type": "application/json",
            },
            timeout=120.0,
        )

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
        """Send a chat completion request and return a standardised result."""
        payload: dict = {
            "model": model,
            "messages": messages,
            "stream": stream,
        }
        if tools:
            payload["tools"] = self._convert_tools(tools)

        try:
            resp = await self.client.post("/chat/completions", json=payload)
            resp.raise_for_status()
            data = resp.json()
        except httpx.HTTPStatusError as exc:
            return self._error_response(
                f"OpenRouter HTTP {exc.response.status_code}: {exc.response.text}"
            )
        except httpx.ConnectError:
            return self._error_response("Cannot connect to OpenRouter API.")
        except Exception as exc:  # noqa: BLE001
            return self._error_response(f"OpenRouter error: {exc}")

        choice = (data.get("choices") or [{}])[0]
        message = choice.get("message", {})

        content = message.get("content", "") or ""
        tool_calls = self._parse_tool_calls(message.get("tool_calls"))

        raw_usage = data.get("usage", {})
        usage = {
            "input_tokens": raw_usage.get("prompt_tokens", 0) or 0,
            "output_tokens": raw_usage.get("completion_tokens", 0) or 0,
        }

        return {"content": content, "tool_calls": tool_calls, "usage": usage}

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _convert_tools(tools: list[dict]) -> list[dict]:
        """Ensure tools are in OpenAI function-calling format."""
        converted: list[dict] = []
        for tool in tools:
            if "type" in tool and tool["type"] == "function" and "function" in tool:
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
        """Parse OpenAI-style tool_calls into the standardised format."""
        if not raw_calls:
            return []

        parsed: list[dict] = []
        for call in raw_calls:
            func = call.get("function", {})
            arguments = func.get("arguments", "{}")
            if isinstance(arguments, str):
                try:
                    arguments = json.loads(arguments)
                except json.JSONDecodeError:
                    arguments = {"raw": arguments}
            parsed.append(
                {
                    "id": call.get("id", ""),
                    "name": func.get("name", ""),
                    "arguments": arguments,
                }
            )
        return parsed

    @staticmethod
    def _error_response(msg: str) -> dict:
        return {
            "content": msg,
            "tool_calls": [],
            "usage": {"input_tokens": 0, "output_tokens": 0},
        }
