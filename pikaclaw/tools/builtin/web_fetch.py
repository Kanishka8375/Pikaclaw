"""Web fetch tool."""
from __future__ import annotations

import re


class WebFetchTool:
    """Fetch content from a URL."""

    name = "WebFetch"
    description = "Fetch a web page and return its text content (HTML tags stripped)."
    parameters = {
        "type": "object",
        "properties": {
            "url": {"type": "string", "description": "The URL to fetch."},
        },
        "required": ["url"],
    }

    async def execute(self, params: dict) -> str:
        try:
            import httpx
        except ImportError:
            return "Error: httpx is not installed. Run: pip install httpx"

        try:
            url = params["url"]

            async with httpx.AsyncClient(follow_redirects=True, timeout=20) as client:
                resp = await client.get(
                    url,
                    headers={"User-Agent": "Mozilla/5.0 (compatible; Pikaclaw/1.0)"},
                )
                resp.raise_for_status()

            text = resp.text
            # Strip HTML tags
            text = re.sub(r"<script[^>]*>.*?</script>", "", text, flags=re.DOTALL)
            text = re.sub(r"<style[^>]*>.*?</style>", "", text, flags=re.DOTALL)
            text = re.sub(r"<[^>]+>", " ", text)
            # Collapse whitespace
            text = re.sub(r"\s+", " ", text).strip()

            # Truncate to 50KB
            max_bytes = 50 * 1024
            if len(text) > max_bytes:
                text = text[:max_bytes] + "\n\n[Content truncated at 50KB]"

            return text if text else "No content found at URL."
        except Exception as e:
            return f"Error fetching URL: {e}"
