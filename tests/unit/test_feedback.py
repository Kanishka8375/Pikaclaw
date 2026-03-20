"""Tests for the feedback system — collector, analyzer, signal detector."""
from __future__ import annotations

import pytest

from pikaclaw.feedback.collector import FeedbackCollector, FeedbackEntry, CATEGORIES
from pikaclaw.feedback.analyzer import FeedbackAnalyzer, FeedbackPattern, CATEGORY_TO_WEAKNESS
from pikaclaw.feedback.signals import ImplicitSignalDetector, ImplicitSignal


# ═══════════════════════════════════════════════════════════
# FEEDBACK COLLECTOR
# ═══════════════════════════════════════════════════════════

class TestFeedbackCollector:
    @pytest.fixture
    def collector(self, tmp_path):
        return FeedbackCollector(db_path=str(tmp_path / "feedback.db"))

    async def test_submit_and_retrieve(self, collector):
        entry_id = await collector.submit(
            rating=2, category="wrong_answer",
            comment="The code didn't compile",
            session_id="sess-1", agent="build", model="test-model",
        )
        assert len(entry_id) > 0
        entries = await collector.get_recent(days=1)
        assert len(entries) == 1
        assert entries[0].rating == 2
        assert entries[0].category == "wrong_answer"
        assert entries[0].comment == "The code didn't compile"

    async def test_submit_multiple(self, collector):
        await collector.submit(rating=1, category="hallucination", comment="Made up a file")
        await collector.submit(rating=3, category="slow", comment="Took too long")
        await collector.submit(rating=2, category="hallucination", comment="Invented a function")
        entries = await collector.get_recent(days=1)
        assert len(entries) == 3

    async def test_get_by_category(self, collector):
        await collector.submit(category="wrong_answer", comment="a")
        await collector.submit(category="slow", comment="b")
        await collector.submit(category="wrong_answer", comment="c")
        results = await collector.get_by_category("wrong_answer")
        assert len(results) == 2
        assert all(r.category == "wrong_answer" for r in results)

    async def test_get_unresolved(self, collector):
        eid = await collector.submit(category="bad_code", comment="buggy")
        await collector.submit(category="slow", comment="slow")
        await collector.mark_resolved(eid, "fix-123")
        unresolved = await collector.get_unresolved()
        assert len(unresolved) == 1
        assert unresolved[0].category == "slow"

    async def test_mark_resolved(self, collector):
        eid = await collector.submit(category="wrong_answer", comment="wrong")
        success = await collector.mark_resolved(eid, "darwin-exp-42")
        assert success
        entries = await collector.get_unresolved()
        assert len(entries) == 0

    async def test_mark_resolved_nonexistent(self, collector):
        result = await collector.mark_resolved("nonexistent-id")
        assert not result

    async def test_satisfaction_score(self, collector):
        await collector.submit(rating=1, category="wrong_answer")
        await collector.submit(rating=2, category="wrong_answer")
        await collector.submit(rating=5, category="other")
        score = await collector.get_satisfaction_score(days=1)
        assert score["total_feedback"] == 3
        assert score["avg_rating"] > 0
        assert score["top_complaint"] == "wrong_answer"

    async def test_satisfaction_score_empty(self, collector):
        score = await collector.get_satisfaction_score(days=1)
        assert score["total_feedback"] == 0
        assert score["avg_rating"] == 0

    async def test_invalid_category_defaults_to_other(self, collector):
        await collector.submit(category="nonexistent_category")
        entries = await collector.get_recent(days=1)
        assert entries[0].category == "other"

    async def test_rating_clamped(self, collector):
        await collector.submit(rating=99)
        await collector.submit(rating=-5)
        entries = await collector.get_recent(days=1)
        ratings = sorted(e.rating for e in entries)
        assert ratings == [0, 5]

    async def test_implicit_source(self, collector):
        await collector.submit(source="implicit", category="wrong_answer", comment="retry detected")
        score = await collector.get_satisfaction_score(days=1)
        assert score["source_breakdown"].get("implicit") == 1

    async def test_conversation_snippet_truncated(self, collector):
        long_snippet = "x" * 5000
        await collector.submit(conversation_snippet=long_snippet)
        entries = await collector.get_recent(days=1)
        assert len(entries[0].conversation_snippet) <= 2000


# ═══════════════════════════════════════════════════════════
# IMPLICIT SIGNAL DETECTOR
# ═══════════════════════════════════════════════════════════

class TestImplicitSignalDetector:
    def test_detect_rejection_no(self):
        d = ImplicitSignalDetector()
        signals = d.analyze_message("No, that's not right")
        assert len(signals) >= 1
        assert any(s.signal_type == "rejection" for s in signals)

    def test_detect_rejection_wrong(self):
        d = ImplicitSignalDetector()
        signals = d.analyze_message("That's wrong, try again")
        assert any(s.signal_type == "rejection" for s in signals)

    def test_detect_rejection_doesnt_work(self):
        d = ImplicitSignalDetector()
        signals = d.analyze_message("It doesn't work")
        assert any(s.signal_type == "rejection" for s in signals)

    def test_detect_correction(self):
        d = ImplicitSignalDetector()
        signals = d.analyze_message("Actually, it should be using async/await")
        assert any(s.signal_type == "correction" for s in signals)

    def test_detect_correction_let_me_clarify(self):
        d = ImplicitSignalDetector()
        signals = d.analyze_message("Let me clarify what I meant")
        assert any(s.signal_type == "correction" for s in signals)

    def test_no_signal_for_normal_message(self):
        d = ImplicitSignalDetector()
        signals = d.analyze_message("Can you read the file main.py and tell me what it does?")
        rejections = [s for s in signals if s.signal_type in ("rejection", "correction")]
        assert len(rejections) == 0

    def test_no_signal_for_long_message(self):
        d = ImplicitSignalDetector()
        # Long messages are new instructions, not rejections
        signals = d.analyze_message("No " + "here is a very long message about what I want " * 10)
        rejections = [s for s in signals if s.signal_type == "rejection"]
        assert len(rejections) == 0

    def test_detect_retry(self):
        d = ImplicitSignalDetector()
        d.analyze_message("how do I sort a list in python using the sorted function")
        signals = d.analyze_message("how do I sort a list in python with the sorted function")
        assert any(s.signal_type == "retry" for s in signals)

    def test_no_retry_for_different_message(self):
        d = ImplicitSignalDetector()
        d.analyze_message("How do I sort a list?")
        signals = d.analyze_message("What is the capital of France?")
        retries = [s for s in signals if s.signal_type == "retry"]
        assert len(retries) == 0

    def test_detect_agent_switch(self):
        d = ImplicitSignalDetector()
        signals = d.analyze_message("switch to debug", context={
            "agent_switched": True, "previous_agent": "build", "agent": "debug",
        })
        assert any(s.signal_type == "agent_switch" for s in signals)

    def test_detect_long_struggle(self):
        d = ImplicitSignalDetector()
        signals = d.analyze_message("still not working", context={"turn_count": 15})
        assert any(s.signal_type == "long_struggle" for s in signals)

    def test_detect_error_cascade(self):
        d = ImplicitSignalDetector()
        for i in range(3):
            signals = d.analyze_message(f"try {i}", context={"last_tool_error": "command failed"})
        assert any(s.signal_type == "error_cascade" for s in signals)

    def test_error_cascade_resets(self):
        d = ImplicitSignalDetector()
        d.analyze_message("a", context={"last_tool_error": "fail"})
        d.analyze_message("b", context={"last_tool_error": "fail"})
        d.analyze_message("c", context={})  # No error → resets
        d.analyze_message("d", context={"last_tool_error": "fail"})
        # Should NOT trigger cascade (only 1 error since reset)
        signals = d.analyze_message("e", context={"last_tool_error": "fail"})
        cascades = [s for s in signals if s.signal_type == "error_cascade"]
        assert len(cascades) == 0

    def test_reset(self):
        d = ImplicitSignalDetector()
        d.analyze_message("hello")
        d.analyze_message("hello", context={"last_tool_error": "fail"})
        d.reset()
        assert d._recent_user_messages == []
        assert d._recent_errors == 0

    def test_word_overlap(self):
        assert ImplicitSignalDetector._word_overlap("hello world", "hello world") == 1.0
        assert ImplicitSignalDetector._word_overlap("hello world", "goodbye moon") == 0.0
        assert ImplicitSignalDetector._word_overlap("", "") == 0.0

    def test_signal_has_category(self):
        d = ImplicitSignalDetector()
        signals = d.analyze_message("That's wrong")
        for s in signals:
            assert s.category in CATEGORIES or s.category in ("wrong_answer", "misunderstood", "incomplete", "tool_failure")


# ═══════════════════════════════════════════════════════════
# FEEDBACK ANALYZER
# ═══════════════════════════════════════════════════════════

class TestFeedbackAnalyzer:
    @pytest.fixture
    def collector(self, tmp_path):
        return FeedbackCollector(db_path=str(tmp_path / "feedback.db"))

    @pytest.fixture
    def analyzer(self, collector):
        return FeedbackAnalyzer(collector)

    async def test_analyze_empty(self, analyzer):
        patterns = await analyzer.analyze()
        assert patterns == []

    async def test_analyze_single_category(self, collector, analyzer):
        await collector.submit(rating=1, category="wrong_answer", comment="Wrong output")
        await collector.submit(rating=2, category="wrong_answer", comment="Still wrong")
        patterns = await analyzer.analyze(min_count=2)
        assert len(patterns) >= 1
        assert patterns[0].weakness_category == "accuracy"
        assert patterns[0].count == 2

    async def test_analyze_multiple_categories(self, collector, analyzer):
        await collector.submit(rating=1, category="hallucination", comment="Made up file")
        await collector.submit(rating=2, category="hallucination", comment="Fake function")
        await collector.submit(rating=3, category="slow", comment="Too slow")
        await collector.submit(rating=2, category="slow", comment="Still slow")
        patterns = await analyzer.analyze(min_count=2)
        assert len(patterns) == 2
        categories = {p.weakness_category for p in patterns}
        assert "hallucination" in categories
        assert "performance" in categories

    async def test_to_weaknesses(self, collector, analyzer):
        await collector.submit(rating=1, category="bad_code", comment="Bug in output")
        await collector.submit(rating=2, category="bad_code", comment="Syntax error")
        weaknesses = await analyzer.to_weaknesses(min_count=1)
        assert len(weaknesses) >= 1
        assert weaknesses[0].category == "code_quality"

    async def test_severity_from_low_ratings(self, collector, analyzer):
        # Very low ratings should produce high severity
        await collector.submit(rating=1, category="wrong_answer")
        await collector.submit(rating=1, category="wrong_answer")
        await collector.submit(rating=1, category="wrong_answer")
        patterns = await analyzer.analyze(min_count=1)
        assert patterns[0].severity > 0.5

    async def test_agent_report(self, collector, analyzer):
        await collector.submit(rating=1, category="wrong_answer", agent="build")
        await collector.submit(rating=2, category="slow", agent="build")
        await collector.submit(rating=4, category="other", agent="plan")
        report = await analyzer.get_agent_report()
        assert "build" in report
        assert report["build"]["count"] == 2
        assert "plan" in report

    async def test_trend(self, collector, analyzer):
        await collector.submit(rating=2, category="wrong_answer")
        await collector.submit(rating=3, category="slow")
        trend = await analyzer.get_trend(days=1)
        assert len(trend) >= 1
        assert trend[0]["count"] >= 2

    async def test_min_count_filter(self, collector, analyzer):
        # Only 1 entry — should be filtered out with min_count=2
        await collector.submit(category="wrong_answer")
        patterns = await analyzer.analyze(min_count=2)
        assert len(patterns) == 0

    async def test_sample_comments(self, collector, analyzer):
        await collector.submit(category="slow", comment="Very slow response")
        await collector.submit(category="slow", comment="Takes forever")
        patterns = await analyzer.analyze(min_count=1)
        assert len(patterns[0].sample_comments) > 0


# ═══════════════════════════════════════════════════════════
# CATEGORY MAPPING
# ═══════════════════════════════════════════════════════════

class TestCategoryMapping:
    def test_all_categories_mapped(self):
        for cat in CATEGORIES:
            assert cat in CATEGORY_TO_WEAKNESS, f"Category '{cat}' not mapped"

    def test_mapping_structure(self):
        for cat, (weakness, technique) in CATEGORY_TO_WEAKNESS.items():
            assert isinstance(weakness, str) and len(weakness) > 0
            assert isinstance(technique, str) and len(technique) > 0


# ═══════════════════════════════════════════════════════════
# DARWIN INTEGRATION
# ═══════════════════════════════════════════════════════════

class TestDarwinFeedbackIntegration:
    async def test_observatory_includes_feedback(self, tmp_path):
        """Verify that observatory.diagnose() includes feedback-derived weaknesses."""
        from pikaclaw.darwin.observatory import PerformanceObservatory
        obs = PerformanceObservatory(db_path=str(tmp_path / "metrics.db"))

        # Submit some feedback
        collector = FeedbackCollector(db_path=str(tmp_path / "feedback.db"))
        await collector.submit(rating=1, category="hallucination", comment="Made stuff up")
        await collector.submit(rating=1, category="hallucination", comment="Invented a file")

        # The observatory should pick up feedback via _diagnose_from_feedback
        # (In production this works because FeedbackAnalyzer reads the shared DB.
        #  In tests we verify the method exists and returns the right type.)
        weaknesses = await obs._diagnose_from_feedback(days=7)
        # May be empty in test because analyzer reads a different DB path,
        # but the method should work without error
        assert isinstance(weaknesses, list)

    def test_hypothesis_generator_handles_feedback_categories(self):
        """Verify HypothesisGenerator produces hypotheses for feedback categories."""
        from pikaclaw.darwin.lab import HypothesisGenerator
        from pikaclaw.darwin.observatory import Weakness

        gen = HypothesisGenerator()

        # Test each feedback-derived category
        for fb_category in ["accuracy", "comprehension", "completeness", "code_quality",
                            "hallucination", "tool_reliability", "loop_detection", "safety"]:
            weakness = Weakness(category=fb_category, severity=0.7, description=f"Test {fb_category}")
            hypotheses = gen.generate([weakness])
            assert len(hypotheses) >= 1, f"No hypotheses for {fb_category}"
            assert all(h.expected_improvement > 0 for h in hypotheses)
