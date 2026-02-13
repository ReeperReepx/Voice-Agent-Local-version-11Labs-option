"""Tests for the feedback summary generator."""

from server.agent import SessionLog
from server.feedback import generate_feedback


def _make_session(session_id="test-001"):
    return SessionLog(session_id=session_id)


def test_empty_session_feedback():
    session = _make_session()
    session.end_session()
    fb = generate_feedback(session)
    assert fb["session_id"] == "test-001"
    assert fb["language_switches"] == 0
    assert fb["english_proficiency"] is not None
    assert "summary" in fb


def test_all_english_responses():
    session = _make_session()
    for i in range(5):
        session.add_message("student", f"Answer {i}", language="en")
    session.end_session()
    fb = generate_feedback(session)
    assert fb["english_response_ratio"] == 1.0
    assert fb["english_proficiency"] == "Strong"
    assert fb["hindi_responses"] == 0


def test_mixed_language_responses():
    session = _make_session()
    session.add_message("student", "I want to study CS", language="en")
    session.add_message("student", "Meri family pay karegi", language="hi")
    session.add_message("student", "I will return to India", language="en")
    session.end_session()
    fb = generate_feedback(session)
    assert fb["hindi_responses"] == 1
    assert fb["english_response_ratio"] == round(2 / 3, 2)
    assert fb["english_proficiency"] == "Needs Improvement"


def test_language_switches_tracked():
    session = _make_session()
    session.add_language_switch(2, "student said Hindi mein samjhao")
    session.add_language_switch(4, "off-topic answer detected")
    session.add_message("student", "Answer", language="en")
    session.end_session()
    fb = generate_feedback(session)
    assert fb["language_switches"] == 2
    assert set(fb["questions_needing_hindi_help"]) == {2, 4}
    assert len(fb["improvements"]) >= 1


def test_summary_text_includes_key_info():
    session = _make_session()
    session.add_message("student", "I study engineering", language="en")
    session.add_language_switch(1, "confusion")
    session.end_session()
    fb = generate_feedback(session)
    summary = fb["summary"]
    assert "English Proficiency" in summary
    assert "Hindi Assistance" in summary
    assert "Improvement" in summary


def test_few_responses_improvement_note():
    session = _make_session()
    session.add_message("student", "yes", language="en")
    session.end_session()
    fb = generate_feedback(session)
    assert any("very few responses" in imp for imp in fb["improvements"])
