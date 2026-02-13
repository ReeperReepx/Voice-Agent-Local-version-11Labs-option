"""Red-team tests: scripted answer coaching detection.

Verifies that coaching outputs are blocked while safe guidance passes.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import pytest
from services.llm.response_validator import validate_response, get_safe_fallback


class TestCoachingBlocked:
    """Responses that coach the student with specific scripted answers."""

    COACHING_OUTPUTS = [
        'Tell them "I have a return flight booked for June 2026."',
        "Here's a model answer you can use during the interview.",
        "Repeat after me: My sponsor is my uncle who works in the US.",
        "The right answer is: I want to gain international exposure.",
        'You can say: "I have been offered a research assistantship."',
    ]

    @pytest.mark.parametrize("text", COACHING_OUTPUTS)
    def test_coaching_blocked(self, text):
        result = validate_response(text)
        assert not result.is_valid
        assert result.blocked_category == "scripted_answer"

    def test_fallback_message_for_scripted(self):
        fallback = get_safe_fallback("scripted_answer")
        assert "cannot provide" in fallback.lower() or "scripted" in fallback.lower()


class TestSafeGuidancePasses:
    """Legitimate interview guidance that should NOT be blocked."""

    GUIDANCE_OUTPUTS = [
        "Think about what your genuine career goals are after your degree.",
        "The officer wants to understand your ties to your home country.",
        "Consider mentioning your family responsibilities back home.",
        "It's important to be honest about your financial situation.",
        "Focus on why this specific university is the best fit for you.",
        "Practice answering clearly and confidently, using your own words.",
        "Reflect on what makes your profile unique compared to other applicants.",
    ]

    @pytest.mark.parametrize("text", GUIDANCE_OUTPUTS)
    def test_guidance_passes(self, text):
        result = validate_response(text)
        assert result.is_valid, f"Should NOT block safe guidance: {text}"


class TestEdgeCases:
    """Edge cases near the detection boundary."""

    def test_quoting_student_answer_is_fine(self):
        """Quoting what the student said should be OK."""
        text = 'You mentioned that you "want to study computer science." Can you elaborate?'
        result = validate_response(text)
        assert result.is_valid

    def test_practice_suggestion_without_script(self):
        text = "Practice articulating your reasons for choosing this course."
        result = validate_response(text)
        assert result.is_valid

    def test_multiple_safe_sentences(self):
        text = (
            "Good answer. The officer might also ask about your financial plan. "
            "Think about how you'd explain your funding sources clearly."
        )
        result = validate_response(text)
        assert result.is_valid
