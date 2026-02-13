"""Unit tests for LLM response validator."""

import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from services.llm.response_validator import (
    ValidationResult,
    get_safe_fallback,
    validate_response,
)


class TestBlockScriptedAnswers:
    """Validator must block scripted answer coaching."""

    def test_blocks_direct_script(self):
        result = validate_response('You should say "I plan to return to India after my studies"')
        assert not result.is_valid
        assert result.blocked_category == "scripted_answer"

    def test_blocks_perfect_answer(self):
        result = validate_response("Here's the perfect answer for this question:")
        assert not result.is_valid
        assert result.blocked_category == "scripted_answer"

    def test_blocks_memorize(self):
        result = validate_response("Memorize this response and say it exactly like this")
        assert not result.is_valid
        assert result.blocked_category == "scripted_answer"

    def test_blocks_model_answer(self):
        result = validate_response("Here's a model answer you can use:")
        assert not result.is_valid
        assert result.blocked_category == "scripted_answer"

    def test_blocks_just_say(self):
        result = validate_response('Just say: "My father is sponsoring my education"')
        assert not result.is_valid
        assert result.blocked_category == "scripted_answer"

    def test_allows_guidance(self):
        """Guidance about what to focus on is OK."""
        result = validate_response(
            "Focus on explaining your specific career goals and how this program helps achieve them."
        )
        assert result.is_valid

    def test_allows_feedback(self):
        result = validate_response(
            "Your answer could be stronger if you mentioned your family ties back home."
        )
        assert result.is_valid


class TestBlockLegalAdvice:
    """Validator must block immigration and legal advice."""

    def test_blocks_green_card_advice(self):
        result = validate_response("You should apply for a green card after graduation")
        assert not result.is_valid
        assert result.blocked_category == "legal_advice"

    def test_blocks_pr_advice(self):
        result = validate_response("You can get permanent residency through the express entry")
        assert not result.is_valid
        assert result.blocked_category == "legal_advice"

    def test_blocks_lawyer_recommendation(self):
        result = validate_response("You should hire an immigration consultant to help")
        assert not result.is_valid
        assert result.blocked_category == "legal_advice"

    def test_blocks_legal_guarantee(self):
        result = validate_response("I guarantee that your visa will be approved")
        assert not result.is_valid
        assert result.blocked_category == "legal_advice"

    def test_blocks_visa_law_reference(self):
        result = validate_response("Under section 214b of the immigration law")
        assert not result.is_valid
        assert result.blocked_category == "legal_advice"

    def test_allows_general_info(self):
        result = validate_response(
            "Visa officers typically look for clear return intent and strong home ties."
        )
        assert result.is_valid


class TestBlockHallucinations:
    """Validator must block fabricated specific facts."""

    def test_blocks_specific_fee(self):
        result = validate_response("The visa fee is exactly $350 for F-1 applications")
        assert not result.is_valid
        assert result.blocked_category == "hallucination"

    def test_blocks_processing_time(self):
        result = validate_response("Processing time is exactly 45 days for student visas")
        assert not result.is_valid
        assert result.blocked_category == "hallucination"

    def test_blocks_approval_rate(self):
        result = validate_response("The success rate is 85% for Indian applicants")
        assert not result.is_valid
        assert result.blocked_category == "hallucination"

    def test_blocks_embassy_always_claim(self):
        result = validate_response("The embassy always asks about your family income first")
        assert not result.is_valid
        assert result.blocked_category == "hallucination"

    def test_blocks_data_reference(self):
        result = validate_response("According to our data, most applicants from India get approved")
        assert not result.is_valid
        assert result.blocked_category == "hallucination"

    def test_allows_general_patterns(self):
        result = validate_response(
            "Officers commonly ask about financial arrangements and return plans."
        )
        assert result.is_valid


class TestValidResponses:
    """Test that valid examiner responses pass validation."""

    def test_question_passes(self):
        result = validate_response("Can you tell me more about your financial sponsor?")
        assert result.is_valid

    def test_feedback_passes(self):
        result = validate_response(
            "Your answer about return intent could be stronger. "
            "Consider mentioning specific career opportunities in your home country."
        )
        assert result.is_valid

    def test_encouragement_passes(self):
        result = validate_response("Good answer. Let's move on to the next question.")
        assert result.is_valid

    def test_explanation_passes(self):
        result = validate_response(
            "This question is checking whether you have genuine intent to return. "
            "Officers want to hear about concrete plans and ties."
        )
        assert result.is_valid


class TestSafeFallback:
    """Test fallback responses."""

    def test_scripted_fallback(self):
        fallback = get_safe_fallback("scripted_answer")
        assert "cannot provide" in fallback.lower() or "scripted" in fallback.lower()

    def test_legal_fallback(self):
        fallback = get_safe_fallback("legal_advice")
        assert "legal" in fallback.lower() or "immigration" in fallback.lower()

    def test_hallucination_fallback(self):
        fallback = get_safe_fallback("hallucination")
        assert "official" in fallback.lower() or "rephrase" in fallback.lower()

    def test_unknown_fallback(self):
        fallback = get_safe_fallback("unknown")
        assert len(fallback) > 0
