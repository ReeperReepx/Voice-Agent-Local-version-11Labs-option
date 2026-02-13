"""Tests for the agent session management."""

from server.agent import SessionLog, build_system_prompt


def test_session_log_creation():
    session = SessionLog(session_id="abc")
    assert session.session_id == "abc"
    assert session.transcript == []
    assert session.language_switches == []


def test_add_message():
    session = SessionLog(session_id="abc")
    session.add_message("student", "Hello", language="en")
    assert len(session.transcript) == 1
    assert session.transcript[0]["role"] == "student"
    assert session.transcript[0]["text"] == "Hello"
    assert session.student_language_usage["english"] == 1


def test_add_hindi_message_counts():
    session = SessionLog(session_id="abc")
    session.add_message("student", "Mera naam Preet hai", language="hi")
    assert session.student_language_usage["hindi"] == 1
    assert session.student_language_usage["english"] == 0


def test_add_language_switch():
    session = SessionLog(session_id="abc")
    session.add_language_switch(1, "student confused")
    assert len(session.language_switches) == 1
    assert session.language_switches[0]["question_id"] == 1


def test_session_duration():
    session = SessionLog(session_id="abc")
    session.end_session()
    assert session.duration_minutes() >= 0


def test_to_dict():
    session = SessionLog(session_id="abc")
    session.add_message("agent", "Welcome", language="en")
    d = session.to_dict()
    assert d["session_id"] == "abc"
    assert "transcript" in d
    assert "language_switches" in d
    assert "student_language_usage" in d


def test_system_prompt_contains_questions():
    prompt = build_system_prompt()
    assert "Why have you chosen to study" in prompt
    assert "How will you fund" in prompt
    assert "Hindi hint:" in prompt
    assert "visa officer" in prompt.lower()
