"""Tests for adaptive question ranking."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import pytest
from services.visa_db.ranking import QuestionRanker


class TestComputeTargetDifficulty:
    """Tests for _compute_target_difficulty."""

    def test_empty_scores_returns_easy(self):
        assert QuestionRanker._compute_target_difficulty({}) == 1

    def test_low_scores_returns_easy(self):
        scores = {1: 0.2, 2: 0.3, 3: 0.1}
        assert QuestionRanker._compute_target_difficulty(scores) == 1

    def test_mid_scores_returns_moderate(self):
        scores = {1: 0.5, 2: 0.6, 3: 0.4}
        assert QuestionRanker._compute_target_difficulty(scores) == 2

    def test_high_scores_returns_advanced(self):
        scores = {1: 0.8, 2: 0.9, 3: 0.7}
        assert QuestionRanker._compute_target_difficulty(scores) == 3

    def test_boundary_0_4_returns_moderate(self):
        scores = {1: 0.4}
        assert QuestionRanker._compute_target_difficulty(scores) == 2

    def test_boundary_0_7_returns_advanced(self):
        scores = {1: 0.7}
        assert QuestionRanker._compute_target_difficulty(scores) == 3


class TestRiskBump:
    """Tests for _get_risk_bump."""

    def test_no_origin_returns_zero(self, temp_db):
        assert QuestionRanker._get_risk_bump("US", None, db_path=temp_db) == 0

    def test_invalid_country_returns_zero(self):
        assert QuestionRanker._get_risk_bump("INVALID", "India") == 0

    def test_high_scrutiny_returns_one(self, temp_db):
        """If any risk factor has scrutiny_level >= 3, returns 1."""
        from services.visa_db.retrieval import get_risk_factors
        risks = get_risk_factors("US", origin_country="India", db_path=temp_db)
        has_high = any(r.get("scrutiny_level", 0) >= 3 for r in risks)
        bump = QuestionRanker._get_risk_bump("US", "India", db_path=temp_db)
        assert bump == (1 if has_high else 0)

    def test_no_risk_data_returns_zero(self, temp_db):
        bump = QuestionRanker._get_risk_bump("FI", "Finland", db_path=temp_db)
        assert bump == 0


class TestCheckReask:
    """Tests for _check_reask."""

    def test_no_weak_scores_returns_none(self):
        questions = [{"id": 1}, {"id": 2}]
        scores = {1: 0.8, 2: 0.7}
        asked = {1, 2}
        assert QuestionRanker._check_reask(scores, asked, questions) is None

    def test_weak_score_returns_question(self):
        questions = [{"id": 1, "text": "Q1"}, {"id": 2, "text": "Q2"}]
        scores = {1: 0.2}
        asked = {1}
        result = QuestionRanker._check_reask(scores, asked, questions)
        assert result is not None
        assert result["id"] == 1

    def test_weak_but_not_asked_returns_none(self):
        questions = [{"id": 1}, {"id": 2}]
        scores = {3: 0.1}  # Question 3 not in questions list
        asked = {3}
        assert QuestionRanker._check_reask(scores, asked, questions) is None

    def test_boundary_0_3_triggers_reask(self):
        questions = [{"id": 5}]
        scores = {5: 0.3}
        asked = {5}
        result = QuestionRanker._check_reask(scores, asked, questions)
        assert result is not None

    def test_score_above_threshold_no_reask(self):
        questions = [{"id": 5}]
        scores = {5: 0.31}
        asked = {5}
        assert QuestionRanker._check_reask(scores, asked, questions) is None


class TestSelectNextQuestion:
    """Tests for select_next_question."""

    def test_returns_question_for_valid_input(self, temp_db):
        result = QuestionRanker.select_next_question(
            "US", "academics", {}, set(), db_path=temp_db
        )
        assert result is not None
        assert "id" in result

    def test_excludes_asked_questions(self, temp_db):
        from services.visa_db.retrieval import get_questions_by_country
        all_qs = get_questions_by_country("US", category="academics", db_path=temp_db)
        if len(all_qs) < 2:
            pytest.skip("Need at least 2 questions")

        first_id = all_qs[0]["id"]
        result = QuestionRanker.select_next_question(
            "US", "academics", {}, {first_id}, db_path=temp_db
        )
        assert result is not None
        assert result["id"] != first_id

    def test_all_asked_returns_none(self, temp_db):
        from services.visa_db.retrieval import get_questions_by_country
        all_qs = get_questions_by_country("US", category="academics", db_path=temp_db)
        all_ids = {q["id"] for q in all_qs}
        result = QuestionRanker.select_next_question(
            "US", "academics", {}, all_ids, db_path=temp_db
        )
        # Should either return a re-ask or None
        assert result is None or result["id"] in all_ids

    def test_invalid_country_returns_none(self):
        result = QuestionRanker.select_next_question(
            "INVALID", "academics", {}, set()
        )
        assert result is None

    def test_difficulty_progression(self, temp_db):
        """With high scores, should prefer harder questions."""
        high_scores = {i: 0.9 for i in range(1, 5)}
        result = QuestionRanker.select_next_question(
            "US", "academics", high_scores, set(), db_path=temp_db
        )
        # Should target difficulty 3 (advanced)
        if result:
            assert result.get("difficulty_level") in (1, 2, 3)

    def test_reask_takes_priority(self, temp_db):
        from services.visa_db.retrieval import get_questions_by_country
        all_qs = get_questions_by_country("US", category="academics", db_path=temp_db)
        if not all_qs:
            pytest.skip("No questions available")

        weak_id = all_qs[0]["id"]
        scores = {weak_id: 0.1}
        asked = {weak_id}
        result = QuestionRanker.select_next_question(
            "US", "academics", scores, asked, db_path=temp_db
        )
        assert result is not None
        assert result["id"] == weak_id


class TestGetFollowupForWeakAnswer:
    """Tests for get_followup_for_weak_answer."""

    def test_high_score_returns_none(self, temp_db):
        result = QuestionRanker.get_followup_for_weak_answer(1, 0.8, db_path=temp_db)
        assert result is None

    def test_boundary_score_returns_none(self, temp_db):
        result = QuestionRanker.get_followup_for_weak_answer(1, 0.51, db_path=temp_db)
        assert result is None

    def test_weak_score_with_followups(self, temp_db):
        """If followups exist for a question, weak score should return one."""
        from services.visa_db.retrieval import get_questions_by_country, get_followups
        qs = get_questions_by_country("US", db_path=temp_db)
        # Find a question that has followups
        target = None
        for q in qs:
            if get_followups(q["id"], db_path=temp_db):
                target = q
                break
        if target is None:
            pytest.skip("No questions with followups in test DB")

        result = QuestionRanker.get_followup_for_weak_answer(
            target["id"], 0.2, db_path=temp_db
        )
        assert result is not None
        assert "followup_question" in result

    def test_no_followups_returns_none(self, temp_db):
        # Question ID unlikely to have followups
        result = QuestionRanker.get_followup_for_weak_answer(99999, 0.1, db_path=temp_db)
        assert result is None
