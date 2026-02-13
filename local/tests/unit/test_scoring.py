"""Unit tests for scoring and contradiction tracking."""

import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from services.orchestrator.scoring import InterviewScorer
from services.orchestrator.contradiction_tracker import ContradictionTracker


class TestScoring:
    """Test interview scoring."""

    def test_record_score(self):
        scorer = InterviewScorer()
        scorer.record_score(1, 0.8, category="finance")
        assert scorer.scores[1].score == 0.8

    def test_score_clamped(self):
        scorer = InterviewScorer()
        scorer.record_score(1, 1.5)
        assert scorer.scores[1].score == 1.0
        scorer.record_score(2, -0.5)
        assert scorer.scores[2].score == 0.0

    def test_average_score(self):
        scorer = InterviewScorer()
        scorer.record_score(1, 0.8)
        scorer.record_score(2, 0.6)
        assert scorer.get_average_score() == pytest.approx(0.7)

    def test_average_score_empty(self):
        scorer = InterviewScorer()
        assert scorer.get_average_score() == 0.0

    def test_update_score(self):
        scorer = InterviewScorer()
        scorer.record_score(1, 0.4)
        scorer.update_score(1, 0.7)
        assert scorer.scores[1].score == 0.7

    def test_category_scores(self):
        scorer = InterviewScorer()
        scorer.record_score(1, 0.8, category="finance")
        scorer.record_score(2, 0.6, category="finance")
        scorer.record_score(3, 0.9, category="intent")
        cats = scorer.get_category_scores()
        assert cats["finance"] == pytest.approx(0.7)
        assert cats["intent"] == pytest.approx(0.9)

    def test_weak_areas(self):
        scorer = InterviewScorer()
        scorer.record_score(1, 0.3, category="finance")
        scorer.record_score(2, 0.8, category="intent")
        weak = scorer.get_weak_areas()
        assert len(weak) == 1
        assert weak[0].question_id == 1

    def test_strong_areas(self):
        scorer = InterviewScorer()
        scorer.record_score(1, 0.3, category="finance")
        scorer.record_score(2, 0.8, category="intent")
        strong = scorer.get_strong_areas()
        assert len(strong) == 1
        assert strong[0].question_id == 2

    def test_mark_contradiction_penalizes(self):
        scorer = InterviewScorer()
        scorer.record_score(1, 0.8)
        scorer.mark_contradiction(1)
        assert scorer.scores[1].score == pytest.approx(0.6)
        assert scorer.scores[1].contradiction_detected is True

    def test_get_contradictions(self):
        scorer = InterviewScorer()
        scorer.record_score(1, 0.8)
        scorer.record_score(2, 0.7)
        scorer.mark_contradiction(1)
        contradictions = scorer.get_contradictions()
        assert len(contradictions) == 1
        assert contradictions[0].question_id == 1

    def test_generate_report(self):
        scorer = InterviewScorer()
        scorer.record_score(1, 0.8, category="finance")
        scorer.record_score(2, 0.3, category="intent")
        report = scorer.generate_report()
        assert "average_score" in report
        assert "readiness" in report
        assert "weak_areas" in report
        assert "contradictions" in report
        assert report["total_questions"] == 2


class TestContradictionTracker:
    """Test contradiction detection."""

    def test_no_contradiction_on_single_answer(self):
        tracker = ContradictionTracker()
        contradictions = tracker.extract_and_track(
            1, "intent", "I will return to my home country after studies"
        )
        assert len(contradictions) == 0

    def test_detect_return_intent_contradiction(self):
        tracker = ContradictionTracker()
        tracker.extract_and_track(
            1, "intent", "I will return to my home country"
        )
        contradictions = tracker.extract_and_track(
            2, "intent", "I plan to stay in the US permanently"
        )
        assert len(contradictions) > 0
        assert "return" in contradictions[0].reason.lower() or "stay" in contradictions[0].reason.lower()

    def test_detect_sponsor_contradiction(self):
        tracker = ContradictionTracker()
        tracker.extract_and_track(
            1, "finance", "My father is funding my education"
        )
        contradictions = tracker.extract_and_track(
            2, "finance", "My uncle is paying for everything"
        )
        assert len(contradictions) > 0

    def test_detect_income_contradiction(self):
        tracker = ContradictionTracker()
        tracker.extract_and_track(
            1, "finance", "My family income is 500,000 per year"
        )
        contradictions = tracker.extract_and_track(
            2, "finance", "Our income is 5,000,000 per year"
        )
        assert len(contradictions) > 0

    def test_no_contradiction_consistent_answers(self):
        tracker = ContradictionTracker()
        tracker.extract_and_track(
            1, "intent", "I will return to India after my studies"
        )
        contradictions = tracker.extract_and_track(
            2, "intent", "I plan to come back to my home country"
        )
        assert len(contradictions) == 0

    def test_has_contradictions(self):
        tracker = ContradictionTracker()
        assert not tracker.has_contradictions()
        tracker.extract_and_track(1, "intent", "I will return home")
        tracker.extract_and_track(2, "intent", "I plan to stay permanently")
        assert tracker.has_contradictions()

    def test_get_all_contradictions(self):
        tracker = ContradictionTracker()
        tracker.extract_and_track(1, "intent", "I will return home")
        tracker.extract_and_track(2, "intent", "I want to settle in the US")
        all_c = tracker.get_all_contradictions()
        assert isinstance(all_c, list)
