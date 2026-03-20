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
        """Generate hypotheses from observed weaknesses and research findings.

        Handles both system-metric weaknesses (reliability, performance, cost)
        and user-feedback weaknesses (accuracy, comprehension, hallucination, etc).
        """
        hypotheses: list[Hypothesis] = []

        for weakness in weaknesses:
            category = getattr(weakness, "category", str(weakness))
            severity = getattr(weakness, "severity", 0.5)
            desc = getattr(weakness, "description", str(weakness))

            generated = _HYPOTHESIS_RECIPES.get(category)
            if generated:
                for recipe in generated:
                    hypotheses.append(Hypothesis(
                        target_weakness=desc,
                        technique=recipe["technique"],
                        mechanism=recipe["mechanism"],
                        expected_improvement=recipe["expected_improvement"] * severity,
                        confidence=recipe["confidence"],
                        description=recipe["description"],
                    ))
            else:
                # Unknown category — generic improvement
                hypotheses.append(Hypothesis(
                    target_weakness=desc,
                    technique="prompt_refinement",
                    mechanism="Refine prompts and behavior based on user feedback",
                    expected_improvement=0.2 * severity,
                    confidence=0.5,
                    description=f"Address '{category}' weakness through prompt tuning",
                ))

        # Sort by priority (confidence * expected_improvement)
        hypotheses.sort(key=lambda h: h.priority, reverse=True)
        return hypotheses


# ─── Hypothesis recipes for each weakness category ───────────────────────
# System-metric categories + feedback-derived categories
_HYPOTHESIS_RECIPES: dict[str, list[dict]] = {
    # === System metrics ===
    "reliability": [
        {"technique": "retry_with_backoff", "mechanism": "Add retry logic with exponential backoff for failed model calls",
         "expected_improvement": 0.3, "confidence": 0.8, "description": "Improve reliability by retrying failed calls"},
        {"technique": "prompt_refinement", "mechanism": "Refine system prompts to reduce ambiguous instructions",
         "expected_improvement": 0.2, "confidence": 0.6, "description": "Reduce failures through better prompting"},
    ],
    "performance": [
        {"technique": "model_routing", "mechanism": "Route simple tasks to faster/smaller models",
         "expected_improvement": 0.4, "confidence": 0.7, "description": "Speed up by using smaller models for simple tasks"},
    ],
    "cost": [
        {"technique": "context_compression", "mechanism": "Compress context before sending to expensive models",
         "expected_improvement": 0.3, "confidence": 0.7, "description": "Reduce cost through context compression"},
    ],

    # === Feedback-derived: user said "wrong answer" ===
    "accuracy": [
        {"technique": "grounding_verification", "mechanism": "Cross-check answers against file content before responding",
         "expected_improvement": 0.4, "confidence": 0.7, "description": "Verify facts against actual code/files before answering"},
        {"technique": "chain_of_thought", "mechanism": "Force step-by-step reasoning before giving final answer",
         "expected_improvement": 0.3, "confidence": 0.65, "description": "Reduce wrong answers through structured reasoning"},
    ],

    # === Feedback-derived: user said "didn't understand me" ===
    "comprehension": [
        {"technique": "intent_parsing", "mechanism": "Add explicit intent classification before acting",
         "expected_improvement": 0.35, "confidence": 0.6, "description": "Better understand user intent before executing"},
        {"technique": "clarification_prompt", "mechanism": "Ask clarifying questions when request is ambiguous",
         "expected_improvement": 0.3, "confidence": 0.7, "description": "Ask before assuming when instructions are unclear"},
    ],

    # === Feedback-derived: user said "incomplete" ===
    "completeness": [
        {"technique": "multi_step_planning", "mechanism": "Plan all steps before executing, verify checklist at end",
         "expected_improvement": 0.4, "confidence": 0.7, "description": "Plan first, execute all steps, verify completion"},
        {"technique": "task_decomposition", "mechanism": "Break complex tasks into explicit subtasks with tracking",
         "expected_improvement": 0.3, "confidence": 0.65, "description": "Decompose tasks so nothing gets missed"},
    ],

    # === Feedback-derived: user said "bad code" ===
    "code_quality": [
        {"technique": "code_review_loop", "mechanism": "Self-review generated code for bugs before presenting",
         "expected_improvement": 0.35, "confidence": 0.7, "description": "Review own code for correctness before submitting"},
        {"technique": "test_generation", "mechanism": "Auto-generate and run tests for written code",
         "expected_improvement": 0.3, "confidence": 0.65, "description": "Write tests to catch bugs before the user does"},
    ],

    # === Feedback-derived: user said "hallucination" ===
    "hallucination": [
        {"technique": "grounding_verification", "mechanism": "Verify all file/function references exist before claiming they do",
         "expected_improvement": 0.5, "confidence": 0.75, "description": "Stop making up files and functions that don't exist"},
        {"technique": "source_citation", "mechanism": "Always reference the actual file and line number",
         "expected_improvement": 0.3, "confidence": 0.7, "description": "Cite sources so claims can be verified"},
    ],

    # === Feedback-derived: user said "tool failure" ===
    "tool_reliability": [
        {"technique": "tool_error_handling", "mechanism": "Better error recovery and fallback when tools fail",
         "expected_improvement": 0.3, "confidence": 0.75, "description": "Gracefully handle tool failures instead of crashing"},
        {"technique": "tool_validation", "mechanism": "Validate tool inputs before execution",
         "expected_improvement": 0.25, "confidence": 0.7, "description": "Check inputs are valid before calling tools"},
    ],

    # === Feedback-derived: user said "repetitive / going in circles" ===
    "loop_detection": [
        {"technique": "conversation_tracking", "mechanism": "Track attempted approaches and avoid repeating failed ones",
         "expected_improvement": 0.4, "confidence": 0.7, "description": "Remember what was already tried and don't repeat it"},
        {"technique": "stuck_detection", "mechanism": "Detect when stuck in a loop and try a different approach",
         "expected_improvement": 0.35, "confidence": 0.65, "description": "Recognize loops and break out with new strategies"},
    ],

    # === Feedback-derived: safety concern ===
    "safety": [
        {"technique": "security_hardening", "mechanism": "Strengthen input validation and output sanitization",
         "expected_improvement": 0.3, "confidence": 0.8, "description": "Harden security checks based on reported incidents"},
    ],
}
