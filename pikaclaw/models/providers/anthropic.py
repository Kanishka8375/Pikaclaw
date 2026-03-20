"""Anthropic API provider."""
from __future__ import annotations

import httpx


class AnthropicProvider:
    """Provider for the Anthropic Messages API."""

    def __init__(self, api_key: str) -> None:
        self.api_key = api_key
        self.client = httpx.AsyncClient(
            base_url="https://api.anthropic.com/v1",
            headers={
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
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
        system: str | None = None,
        stream: bool = False,
    ) -> dict:
        """Send a completion request and return a standardised result dict."""
        payload: dict = {
            "model": model,
            "max_tokens": 8192,
            "messages": messages,
        }
        if system:
            payload["system"] = system
        if tools:
            payload["tools"] = tools

        try:
            resp = await self.client.post("/messages", json=payload)
            resp.raise_for_status()
            data = resp.json()
        except httpx.HTTPStatusError as exc:
            return self._error_response(
                f"Anthropic HTTP {exc.response.status_code}: {exc.response.text}"
            )
        except httpx.ConnectError:
            return self._error_response("Cannot connect to Anthropic API.")
        except Exception as exc:  # noqa: BLE001
            return self._error_response(f"Anthropic error: {exc}")

        content_parts: list[str] = []
        tool_calls: list[dict] = []

        for block in data.get("content", []):
            block_type = block.get("type")
            if block_type == "text":
                content_parts.append(block.get("text", ""))
            elif block_type == "tool_use":
                tool_calls.append(
                    {
                        "id": block.get("id", ""),
                        "name": block.get("name", ""),
                        "arguments": block.get("input", {}),
                    }
                )

        raw_usage = data.get("usage", {})
        usage = {
            "input_tokens": raw_usage.get("input_tokens", 0),
            "output_tokens": raw_usage.get("output_tokens", 0),
        }

        return {
            "content": "\n".join(content_parts),
            "tool_calls": tool_calls,
            "usage": usage,
        }

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _error_response(msg: str) -> dict:
        return {
            "content": msg,
            "tool_calls": [],
            "usage": {"input_tokens": 0, "output_tokens": 0},
        }
