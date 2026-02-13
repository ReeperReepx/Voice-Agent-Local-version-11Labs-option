"""Tests for the visa question bank."""

from server.questions import get_all_questions, get_question_by_id, get_questions_by_category


def test_all_questions_returns_five():
    questions = get_all_questions()
    assert len(questions) == 5


def test_each_question_has_required_fields():
    for q in get_all_questions():
        assert "id" in q
        assert "question_en" in q
        assert "hint_hi" in q
        assert "category" in q
        assert "follow_ups" in q
        assert len(q["follow_ups"]) >= 1


def test_get_question_by_id():
    q = get_question_by_id(1)
    assert q is not None
    assert q["category"] == "study_plans"


def test_get_question_by_id_not_found():
    assert get_question_by_id(999) is None


def test_get_questions_by_category():
    financial = get_questions_by_category("financial")
    assert len(financial) == 1
    assert financial[0]["id"] == 2


def test_questions_cover_all_categories():
    categories = {q["category"] for q in get_all_questions()}
    expected = {"study_plans", "financial", "return_intent", "academic", "english_proficiency"}
    assert categories == expected
