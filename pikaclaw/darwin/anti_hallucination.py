"""Anti-Hallucination Pipeline — verifies response accuracy."""
from __future__ import annotations

import re
from dataclasses import dataclass, field


@dataclass
class Claim:
    """An extracted claim from a response."""
    text: str
    verified: bool = False
    source: str = ""
    confidence: float = 0.0


@dataclass
class VerificationResult:
    """Result of verifying a response against sources."""
    claims: list[Claim] = field(default_factory=list)

    @property
    def verified_count(self) -> int:
        return sum(1 for c in self.claims if c.verified)

    @property
    def unverified_count(self) -> int:
        return sum(1 for c in self.claims if not c.verified)

    @property
    def score(self) -> float:
        if not self.claims:
            return 1.0
        return self.verified_count / len(self.claims)


class AntiHallucinationPipeline:
    """Detects and reduces hallucinations in model responses."""

    def __init__(self, model_router=None):
        self.router = model_router

    def extract_claims(self, response: str) -> list[str]:
        """Extract factual claims from a response."""
        claims: list[str] = []
        sentences = re.split(r"[.!?]+", response)
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence or len(sentence) < 15:
                continue
            # Skip questions and subjective statements
            if sentence.endswith("?"):
                continue
            # Look for factual-sounding statements
            factual_indicators = [
                r"\b(?:is|are|was|were|has|have|contains?|returns?|creates?|uses?)\b",
                r"\b(?:file|function|class|module|method|variable)\b",
                r"\b(?:version|line|error|output|result)\b",
            ]
            for pattern in factual_indicators:
                if re.search(pattern, sentence, re.IGNORECASE):
                    claims.append(sentence)
                    break
        return claims

    def verify_claim_against_source(self, claim: str, source: str) -> tuple[bool, float]:
        """Verify a single claim against a source text.

        Returns (verified, confidence).
        """
        claim_lower = claim.lower()
        source_lower = source.lower()

        # Extract key terms from claim
        words = set(re.findall(r"\b\w{3,}\b", claim_lower))
        # Remove common words
        stop_words = {"the", "and", "for", "are", "but", "not", "you", "all", "can", "this", "that", "with", "from", "have", "has", "was", "were", "will", "been"}
        key_words = words - stop_words

        if not key_words:
            return True, 0.5  # Can't verify, assume ok

        # Count how many key words appear in source
        matches = sum(1 for w in key_words if w in source_lower)
        ratio = matches / len(key_words)

        verified = ratio >= 0.5
        confidence = ratio

        return verified, confidence

    def verify_response(self, response: str, sources: list[str]) -> VerificationResult:
        """Verify a response against provided sources."""
        raw_claims = self.extract_claims(response)
        claims: list[Claim] = []

        combined_source = "\n".join(sources)

        for claim_text in raw_claims:
            verified, confidence = self.verify_claim_against_source(claim_text, combined_source)
            source_ref = ""
            if verified:
                # Find which source contains the most matching content
                best_match = 0
                for i, src in enumerate(sources):
                    _, conf = self.verify_claim_against_source(claim_text, src)
                    if conf > best_match:
                        best_match = conf
                        source_ref = f"source[{i}]"

            claims.append(Claim(
                text=claim_text,
                verified=verified,
                source=source_ref,
                confidence=confidence,
            ))

        return VerificationResult(claims=claims)

    async def chain_of_verification(self, response: str) -> str:
        """Apply chain-of-verification to revise a response.

        If no model router is available, returns the original response.
        """
        if not self.router:
            return response

        try:
            # Step 1: Generate verification questions
            q_response = await self.router.complete(messages=[{
                "role": "user",
                "content": f"List 3 factual claims in this text that could be wrong. For each, write a verification question.\n\nText: {response[:2000]}",
            }])
            questions = q_response.get("content", "")

            # Step 2: Answer verification questions
            a_response = await self.router.complete(messages=[{
                "role": "user",
                "content": f"Answer these verification questions honestly. If unsure, say 'uncertain'.\n\n{questions}",
            }])
            answers = a_response.get("content", "")

            # Step 3: Revise response
            r_response = await self.router.complete(messages=[{
                "role": "user",
                "content": (
                    f"Original response:\n{response[:2000]}\n\n"
                    f"Verification Q&A:\n{answers[:1000]}\n\n"
                    f"Revise the original response to fix any inaccuracies found. Keep it concise."
                ),
            }])
            return r_response.get("content", response)
        except Exception:
            return response
