"""Integration tests for orchestrator + LLM pipeline.

Tests the flow: orchestrator context → LLM prompt → response → validator.
Uses mock LLM responses since the actual model may not be running.
"""

import os
import sys
from unittest.mock import patch

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from services.orchestrator.state_machine import InterviewStateMachine, InterviewState
from services.orchestrator.language_control import LanguageController, Language
from services.orchestrator.scoring import InterviewScorer
from services.llm.qwen_runtime import build_system_prompt, load_template
from services.llm.response_validator import validate_response


class TestPromptBuilding:
    """Test that orchestrator state produces valid prompts."""

    def test_build_prompt_for_greeting(self):
        prompt = build_system_prompt("greeting", "US")
        assert "visa" in prompt.lower()
        assert "greeting" in prompt.lower()
        assert "US" in prompt

    def test_build_prompt_for_finance(self):
        prompt = build_system_prompt("finance", "UK")
        assert "UK" in prompt

    def test_build_prompt_with_explanation_mode(self):
        prompt = build_system_prompt("academics", "US", explanation_mode=True)
        assert "explanation" in prompt.lower()
        assert "hindi" in prompt.lower()

    def test_templates_exist(self):
        base = load_template("base_system.txt")
        tone = load_template("examiner_tone.txt")
        explanation = load_template("explanation_mode.txt")
        assert len(base) > 50
        assert len(tone) > 50
        assert len(explanation) > 50


class TestOrchestratorLLMFlow:
    """Test the full orchestrator → LLM → validator flow with mocked LLM."""

    def _mock_llm_response(self, text: str):
        """Helper to mock LLM generate_response."""
        return text

    def test_valid_examiner_response_accepted(self):
        sm = InterviewStateMachine(destination_country="US")
        scorer = InterviewScorer()

        # Simulate: orchestrator determines state, builds prompt
        state = sm.current_state.value
        prompt = build_system_prompt(state, sm.context.destination_country)

        # Mock LLM response
        mock_response = "Good morning. Welcome to your visa interview practice. Could you please state your name?"

        # Validate
        result = validate_response(mock_response)
        assert result.is_valid

        # Score
        scorer.record_score(1, 0.8, category="greeting")
        assert scorer.get_average_score() == 0.8

    def test_scripted_response_rejected(self):
        mock_response = 'Just say: "I am going to study computer science at MIT"'
        result = validate_response(mock_response)
        assert not result.is_valid
        assert result.blocked_category == "scripted_answer"

    def test_language_control_integrated(self):
        """Language controller output feeds into prompt building."""
        lc = LanguageController()

        # Normal mode
        action = lc.process_input("I want to study in the US")
        assert action["output_language"] == Language.ENGLISH
        prompt = build_system_prompt("academics", "US", explanation_mode=False)
        assert "EXPLANATION MODE" not in prompt

        # Hindi switch
        action = lc.process_input("Hindi mein samjha do")
        assert action["explanation_mode"] is True
        prompt = build_system_prompt("academics", "US", explanation_mode=True)
        assert "explanation" in prompt.lower()

    def test_full_state_advance_with_validation(self):
        """Advance through states with mock responses, all validated."""
        sm = InterviewStateMachine(destination_country="CA")
        scorer = InterviewScorer()

        mock_responses = {
            "greeting": "Welcome. Please tell me your name and which program you are applying for.",
            "academics": "I see. Can you tell me about your academic background in more detail?",
            "course_choice": "Why did you specifically choose this university and program?",
            "finance": "How will you fund your studies and living expenses?",
            "intent": "What are your plans after completing your degree?",
            "country_specific": "Are you aware of the study permit requirements?",
            "summary": "Thank you for completing this practice session.",
        }

        for i, (state_name, response) in enumerate(mock_responses.items()):
            # Validate each response
            result = validate_response(response)
            assert result.is_valid, f"Response for {state_name} was rejected: {result.reason}"

            # Score
            scorer.record_score(i + 1, 0.7, category=state_name)

            # Advance
            if sm.can_advance():
                sm.advance()

        report = scorer.generate_report()
        assert report["total_questions"] == 7
        assert report["average_score"] == 0.7

    def test_respects_language_rule(self):
        """Input language = output language unless explanation mode."""
        lc = LanguageController()

        # English input → English output
        result = lc.process_input("I want to study computer science")
        assert result["output_language"] == Language.ENGLISH

        # Hindi switch request → Hindi output
        result = lc.process_input("Hindi mein samjha do")
        assert result["output_language"] == Language.HINDI

        # Auto revert → back to English
        lc.auto_revert()
        result = lc.process_input("My father is my sponsor")
        assert result["output_language"] == Language.ENGLISH
