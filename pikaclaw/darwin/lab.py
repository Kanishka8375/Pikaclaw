"""Research Lab — scans external sources and generates hypotheses."""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Paper:
    """An academic paper reference."""
    title: str
    authors: str = ""
    summary: str = ""
    url: str = ""
    published: str = ""


@dataclass
class Repo:
    """A GitHub repository reference."""
    name: str
    description: str = ""
    stars: int = 0
    language: str = ""
    url: str = ""


@dataclass
class HFModel:
    """A HuggingFace model reference."""
    model_id: str
    author: str = ""
    downloads: int = 0
    pipeline_tag: str = ""


@dataclass
class Hypothesis:
    """A hypothesis for improving PikaClaw."""
    target_weakness: str
    technique: str
    mechanism: str
    expected_improvement: float  # 0.0 - 1.0
    confidence: float  # 0.0 - 1.0
    description: str = ""

    @property
    def priority(self) -> float:
        return self.confidence * self.expected_improvement


class ResearchLab:
    """Scans external sources for techniques and patterns."""

    def __init__(self):
        self._http = None

    def _get_http(self):
        if self._http is None:
            import httpx
            self._http = httpx.AsyncClient(timeout=30)
        return self._http

    async def scan_arxiv(self, query: str = "AI agent", max_results: int = 5) -> list[Paper]:
        """Search arXiv for relevant papers."""
        try:
            client = self._get_http()
            url = "http://export.arxiv.org/api/query"
            params = {"search_query": f"all:{query}", "max_results": max_results, "sortBy": "submittedDate"}
            response = await client.get(url, params=params)
            response.raise_for_status()

            # Simple XML parsing
            papers: list[Paper] = []
            import xml.etree.ElementTree as ET
            root = ET.fromstring(response.text)
            ns = {"atom": "http://www.w3.org/2005/Atom"}
            for entry in root.findall("atom:entry", ns):
                title = entry.findtext("atom:title", "", ns).strip().replace("\n", " ")
                summary = entry.findtext("atom:summary", "", ns).strip()[:500]
                authors = ", ".join(a.findtext("atom:name", "", ns) for a in entry.findall("atom:author", ns))
                link = ""
                for l in entry.findall("atom:link", ns):
                    if l.get("type") == "text/html":
                        link = l.get("href", "")
                published = entry.findtext("atom:published", "", ns)[:10]
                papers.append(Paper(title=title, authors=authors, summary=summary, url=link, published=published))
            return papers
        except Exception:
            return []

    async def scan_github_trending(self, language: str = "python") -> list[Repo]:
        """Fetch trending repos (via GitHub API search)."""
        try:
            client = self._get_http()
            url = "https://api.github.com/search/repositories"
            params = {"q": f"language:{language} created:>2025-01-01", "sort": "stars", "per_page": 5}
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            return [
                Repo(
                    name=r["full_name"],
                    description=r.get("description", "")[:200],
                    stars=r.get("stargazers_count", 0),
                    language=r.get("language", ""),
                    url=r.get("html_url", ""),
                )
                for r in data.get("items", [])[:5]
            ]
        except Exception:
            return []

    async def scan_huggingface(self, query: str = "code generation") -> list[HFModel]:
        """Search HuggingFace for relevant models."""
        try:
            client = self._get_http()
            url = "https://huggingface.co/api/models"
            params = {"search": query, "limit": 5, "sort": "downloads", "direction": -1}
            response = await client.get(url, params=params)
            response.raise_for_status()
            return [
                HFModel(
                    model_id=m.get("modelId", ""),
                    author=m.get("author", ""),
                    downloads=m.get("downloads", 0),
                    pipeline_tag=m.get("pipeline_tag", ""),
                )
                for m in response.json()[:5]
            ]
        except Exception:
            return []


class HypothesisGenerator:
    """Generates improvement hypotheses from weaknesses and research."""

    def generate(self, weaknesses: list, findings: dict | None = None) -> list[Hypothesis]:
        """Generate hypotheses from observed weaknesses and research findings."""
        hypotheses: list[Hypothesis] = []

        for weakness in weaknesses:
            category = getattr(weakness, "category", str(weakness))
            severity = getattr(weakness, "severity", 0.5)
            desc = getattr(weakness, "description", str(weakness))

            if category == "reliability":
                hypotheses.append(Hypothesis(
                    target_weakness=desc,
                    technique="retry_with_backoff",
                    mechanism="Add retry logic with exponential backoff for failed model calls",
                    expected_improvement=0.3,
                    confidence=0.8,
                    description=f"Improve reliability by retrying failed calls",
                ))
                hypotheses.append(Hypothesis(
                    target_weakness=desc,
                    technique="prompt_refinement",
                    mechanism="Refine system prompts to reduce ambiguous instructions",
                    expected_improvement=0.2,
                    confidence=0.6,
                    description=f"Reduce failures through better prompting",
                ))
            elif category == "performance":
                hypotheses.append(Hypothesis(
                    target_weakness=desc,
                    technique="model_routing",
                    mechanism="Route simple tasks to faster/smaller models",
                    expected_improvement=0.4,
                    confidence=0.7,
                    description=f"Speed up by using smaller models for simple tasks",
                ))
            elif category == "cost":
                hypotheses.append(Hypothesis(
                    target_weakness=desc,
                    technique="context_compression",
                    mechanism="Compress context before sending to expensive models",
                    expected_improvement=0.3,
                    confidence=0.7,
                    description=f"Reduce cost through context compression",
                ))

        # Sort by priority
        hypotheses.sort(key=lambda h: h.priority, reverse=True)
        return hypotheses
