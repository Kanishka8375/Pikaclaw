"""Web search tool using DuckDuckGo."""
from __future__ import annotations

import re
import html


class WebSearchTool:
    """Search the web via DuckDuckGo."""

    name = "WebSearch"
    description = "Search the web using DuckDuckGo and return results with title, URL, and snippet."
    parameters = {
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "Search query."},
            "max_results": {"type": "integer", "description": "Maximum number of results to return.", "default": 5},
        },
        "required": ["query"],
    }

    async def execute(self, params: dict) -> str:
        try:
            import httpx
        except ImportError:
            return "Error: httpx is not installed. Run: pip install httpx"

        try:
            query = params["query"]
            max_results = params.get("max_results", 5)

            async with httpx.AsyncClient(follow_redirects=True, timeout=15) as client:
                resp = await client.get(
                    "https://html.duckduckgo.com/html/",
                    params={"q": query},
                    headers={"User-Agent": "Mozilla/5.0 (compatible; Pikaclaw/1.0)"},
                )
                resp.raise_for_status()

            body = resp.text

            # Parse result blocks
            result_blocks = re.findall(
                r'<a rel="nofollow" class="result__a" href="(.*?)".*?>(.*?)</a>.*?'
                r'<a class="result__snippet".*?>(.*?)</a>',
                body,
                re.DOTALL,
            )

            if not result_blocks:
                return "No search results found."

            results = []
            for url, title, snippet in result_blocks[:max_results]:
                clean_title = re.sub(r"<.*?>", "", html.unescape(title)).strip()
                clean_snippet = re.sub(r"<.*?>", "", html.unescape(snippet)).strip()
                clean_url = html.unescape(url).strip()
                results.append(f"Title: {clean_title}\nURL: {clean_url}\nSnippet: {clean_snippet}\n")

            if not results:
                return "No search results found."

            return "\n".join(results)
        except Exception as e:
            return f"Error searching: {e}"
