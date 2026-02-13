"""Tests for audit logging."""

import json
import os
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import pytest
from unittest.mock import patch, MagicMock
from services.session.audit_log import AuditLogger


@pytest.fixture
def file_logger(tmp_path):
    """Create an AuditLogger that uses file fallback (no Redis)."""
    logger = AuditLogger()
    logger._redis = None  # Force file fallback
    logger._log_dir = tmp_path
    return logger


@pytest.fixture
def mock_redis_logger(tmp_path):
    """Create an AuditLogger with a mocked Redis client."""
    logger = AuditLogger()
    logger._redis = MagicMock()
    logger._log_dir = tmp_path
    return logger


class TestFileLogging:
    """Tests for file-based fallback logging."""

    def test_log_event_creates_file(self, file_logger, tmp_path):
        file_logger.log_event("sess1", "test_event", {"key": "value"})
        log_file = tmp_path / "sess1.jsonl"
        assert log_file.exists()

    def test_log_event_appends_json(self, file_logger, tmp_path):
        file_logger.log_event("sess1", "event_a", {"a": 1})
        file_logger.log_event("sess1", "event_b", {"b": 2})
        log_file = tmp_path / "sess1.jsonl"
        lines = log_file.read_text().strip().split("\n")
        assert len(lines) == 2
        event_a = json.loads(lines[0])
        assert event_a["event_type"] == "event_a"
        event_b = json.loads(lines[1])
        assert event_b["event_type"] == "event_b"

    def test_get_session_log_returns_events(self, file_logger):
        file_logger.log_event("sess2", "start", {})
        file_logger.log_event("sess2", "answer", {"q": 1})
        events = file_logger.get_session_log("sess2")
        assert len(events) == 2
        assert events[0]["event_type"] == "start"
        assert events[1]["event_type"] == "answer"

    def test_get_session_log_empty_session(self, file_logger):
        events = file_logger.get_session_log("nonexistent")
        assert events == []

    def test_event_has_required_fields(self, file_logger):
        file_logger.log_event("sess3", "test", {"foo": "bar"})
        events = file_logger.get_session_log("sess3")
        event = events[0]
        assert "timestamp" in event
        assert event["session_id"] == "sess3"
        assert event["event_type"] == "test"
        assert event["data"] == {"foo": "bar"}

    def test_separate_sessions_separate_files(self, file_logger, tmp_path):
        file_logger.log_event("a", "ev1", {})
        file_logger.log_event("b", "ev2", {})
        assert (tmp_path / "a.jsonl").exists()
        assert (tmp_path / "b.jsonl").exists()
        assert len(file_logger.get_session_log("a")) == 1
        assert len(file_logger.get_session_log("b")) == 1


class TestRedisLogging:
    """Tests for Redis-based logging."""

    def test_log_event_calls_rpush(self, mock_redis_logger):
        mock_redis_logger.log_event("sess1", "answer", {"q": 1})
        mock_redis_logger._redis.rpush.assert_called_once()
        args = mock_redis_logger._redis.rpush.call_args
        assert args[0][0] == "audit:sess1"
        payload = json.loads(args[0][1])
        assert payload["event_type"] == "answer"

    def test_get_session_log_calls_lrange(self, mock_redis_logger):
        entry = json.dumps({
            "timestamp": 1.0,
            "session_id": "s1",
            "event_type": "test",
            "data": {},
        })
        mock_redis_logger._redis.lrange.return_value = [entry]
        events = mock_redis_logger.get_session_log("s1")
        assert len(events) == 1
        mock_redis_logger._redis.lrange.assert_called_once_with("audit:s1", 0, -1)

    def test_redis_failure_falls_back_to_file(self, mock_redis_logger, tmp_path):
        mock_redis_logger._redis.rpush.side_effect = Exception("conn refused")
        mock_redis_logger.log_event("sess_fb", "fallback_event", {})
        log_file = tmp_path / "sess_fb.jsonl"
        assert log_file.exists()


class TestTypedHelpers:
    """Tests for typed logging helpers."""

    def test_log_answer(self, file_logger):
        file_logger.log_answer("s1", question_id=5, answer="My answer", score=0.8, category="finance")
        events = file_logger.get_session_log("s1")
        assert len(events) == 1
        assert events[0]["event_type"] == "answer"
        assert events[0]["data"]["question_id"] == 5
        assert events[0]["data"]["score"] == 0.8

    def test_log_retry(self, file_logger):
        file_logger.log_retry("s1", question_id=3, attempt=2)
        events = file_logger.get_session_log("s1")
        assert events[0]["event_type"] == "retry"
        assert events[0]["data"]["attempt"] == 2

    def test_log_contradiction(self, file_logger):
        file_logger.log_contradiction("s1", question_id=7, reason="income mismatch")
        events = file_logger.get_session_log("s1")
        assert events[0]["event_type"] == "contradiction"
        assert events[0]["data"]["reason"] == "income mismatch"

    def test_log_language_switch(self, file_logger):
        file_logger.log_language_switch("s1", direction="to_hindi", question_id=2)
        events = file_logger.get_session_log("s1")
        assert events[0]["event_type"] == "language_switch"
        assert events[0]["data"]["direction"] == "to_hindi"


class TestIsRedisAvailable:
    """Tests for Redis availability check."""

    def test_no_redis(self, file_logger):
        assert file_logger.is_redis_available is False

    def test_with_redis(self, mock_redis_logger):
        assert mock_redis_logger.is_redis_available is True
