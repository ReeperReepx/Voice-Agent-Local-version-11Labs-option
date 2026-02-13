"""Unit tests for the extracted chat pipeline."""

import os
import sys
from unittest.mock import patch, MagicMock
from dataclasses import dataclass

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from services.orchestrator.chat_pipeline import process_chat_turn, ChatResult
from services.session.session_manager import SessionManager


@pytest.fixture
def session():
    """Create a fresh session for testing."""
    manager = SessionManager()
    return manager.create_session(destination_country="US", origin_country="India")


@pytest.fixture
def mock_audit():
    """Create a mock audit logger."""
    audit = MagicMock()
    audit.log_answer = MagicMock()
    return audit


class TestChatResult:
    """Test ChatResult dataclass."""

    def test_creation(self):
        result = ChatResult(
            response_text="Hello",
            current_state="greeting",
            explanation_mode=False,
            score=0.5,
            output_language="en",
        )
        assert result.response_text == "Hello"
        assert result.current_state == "greeting"
        assert result.explanation_mode is False
        assert result.score == 0.5
        assert result.output_language == "en"


class TestProcessChatTurn:
    """Test the full chat pipeline with mocked LLM."""

    @patch("services.orchestrator.chat_pipeline.generate_response")
    @patch("services.orchestrator.chat_pipeline.validate_response")
    def test_basic_turn(self, mock_validate, mock_llm, session, mock_audit):
        mock_llm.return_value = "Good morning. Tell me about your plans."
        mock_validate.return_value = MagicMock(is_valid=True)

        result = process_chat_turn(session, "Hello, I am here for my visa interview.", mock_audit)

        assert isinstance(result, ChatResult)
        assert result.response_text == "Good morning. Tell me about your plans."
        assert result.current_state == "greeting"
        assert result.explanation_mode is False
        assert result.output_language == "en"
        assert 0.3 <= result.score <= 1.0

    @patch("services.orchestrator.chat_pipeline.generate_response")
    @patch("services.orchestrator.chat_pipeline.validate_response")
    def test_adds_transcript_entries(self, mock_validate, mock_llm, session, mock_audit):
        mock_llm.return_value = "I see."
        mock_validate.return_value = MagicMock(is_valid=True)

        process_chat_turn(session, "My name is Preet.", mock_audit)

        assert len(session.transcript) >= 2
        assert session.transcript[-2]["role"] == "student"
        assert session.transcript[-2]["text"] == "My name is Preet."
        assert session.transcript[-1]["role"] == "agent"
        assert session.transcript[-1]["text"] == "I see."

    @patch("services.orchestrator.chat_pipeline.generate_response")
    @patch("services.orchestrator.chat_pipeline.validate_response")
    def test_audit_logging(self, mock_validate, mock_llm, session, mock_audit):
        mock_llm.return_value = "Understood."
        mock_validate.return_value = MagicMock(is_valid=True)

        process_chat_turn(session, "I plan to study CS at MIT.", mock_audit)

        mock_audit.log_answer.assert_called_once()
        call_kwargs = mock_audit.log_answer.call_args
        assert call_kwargs[1]["answer"] == "I plan to study CS at MIT."

    @patch("services.orchestrator.chat_pipeline.generate_response")
    @patch("services.orchestrator.chat_pipeline.validate_response")
    @patch("services.orchestrator.chat_pipeline.get_safe_fallback")
    def test_invalid_response_gets_fallback(self, mock_fallback, mock_validate, mock_llm, session, mock_audit):
        mock_llm.return_value = "Here is a scripted answer for you..."
        mock_validate.return_value = MagicMock(is_valid=False, blocked_category="scripted")
        mock_fallback.return_value = "I cannot provide scripted answers."

        result = process_chat_turn(session, "What should I say?", mock_audit)

        assert result.response_text == "I cannot provide scripted answers."
        mock_fallback.assert_called_once_with("scripted")

    @patch("services.orchestrator.chat_pipeline.generate_response")
    @patch("services.orchestrator.chat_pipeline.validate_response")
    def test_llm_failure_returns_fallback(self, mock_validate, mock_llm, session, mock_audit):
        mock_llm.side_effect = Exception("Connection refused")
        mock_validate.return_value = MagicMock(is_valid=True)

        result = process_chat_turn(session, "Test input", mock_audit)

        assert "Could you tell me more" in result.response_text

    @patch("services.orchestrator.chat_pipeline.generate_response")
    @patch("services.orchestrator.chat_pipeline.validate_response")
    def test_score_range(self, mock_validate, mock_llm, session, mock_audit):
        mock_llm.return_value = "OK."
        mock_validate.return_value = MagicMock(is_valid=True)

        # Short answer
        result_short = process_chat_turn(session, "Yes", mock_audit)
        assert 0.3 <= result_short.score <= 1.0

        # Long answer
        long_text = " ".join(["word"] * 25)
        result_long = process_chat_turn(session, long_text, mock_audit)
        assert result_long.score >= result_short.score
