"""Unit tests for the interview state machine."""

import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from services.orchestrator.state_machine import (
    InterviewState,
    InterviewStateMachine,
    InvalidTransitionError,
    MAX_QUESTIONS_PER_STATE,
    MAX_RETRIES_PER_QUESTION,
    TRANSITIONS,
)


class TestStateTransitions:
    """Test valid and invalid state transitions."""

    def test_initial_state_is_greeting(self):
        sm = InterviewStateMachine()
        assert sm.current_state == InterviewState.GREETING

    def test_advance_through_all_states(self):
        """State machine advances through all 7 states in order."""
        sm = InterviewStateMachine()
        expected = [
            InterviewState.ACADEMICS,
            InterviewState.COURSE_CHOICE,
            InterviewState.FINANCE,
            InterviewState.INTENT,
            InterviewState.COUNTRY_SPECIFIC,
            InterviewState.SUMMARY,
            InterviewState.ENDED,
        ]
        for expected_state in expected:
            next_state = sm.advance()
            assert next_state == expected_state

    def test_cannot_advance_past_ended(self):
        sm = InterviewStateMachine()
        # Advance to ENDED
        for _ in range(7):
            sm.advance()
        assert sm.is_ended
        with pytest.raises(InvalidTransitionError):
            sm.advance()

    def test_all_transitions_are_defined(self):
        """Every state except ENDED has a transition."""
        for state in InterviewState:
            if state != InterviewState.ENDED:
                assert state in TRANSITIONS

    def test_invalid_backward_jump(self):
        sm = InterviewStateMachine()
        sm.advance()  # Now at ACADEMICS
        sm.advance()  # Now at COURSE_CHOICE
        with pytest.raises(InvalidTransitionError):
            sm.go_to(InterviewState.GREETING)

    def test_valid_forward_jump(self):
        sm = InterviewStateMachine()
        sm.go_to(InterviewState.FINANCE)
        assert sm.current_state == InterviewState.FINANCE

    def test_jump_to_same_state(self):
        sm = InterviewStateMachine()
        sm.go_to(InterviewState.GREETING)  # Same state
        assert sm.current_state == InterviewState.GREETING

    def test_can_advance_returns_true_for_non_ended(self):
        sm = InterviewStateMachine()
        assert sm.can_advance()

    def test_can_advance_returns_false_for_ended(self):
        sm = InterviewStateMachine()
        for _ in range(7):
            sm.advance()
        assert not sm.can_advance()


class TestQuestionTracking:
    """Test question recording and retry logic."""

    def test_record_question(self):
        sm = InterviewStateMachine()
        sm.record_question(1)
        assert sm.context.current_question_id == 1
        assert sm.context.questions_asked_in_state == 1
        assert sm.context.total_questions_asked == 1

    def test_record_multiple_questions(self):
        sm = InterviewStateMachine()
        sm.record_question(1)
        sm.record_question(2)
        assert sm.context.questions_asked_in_state == 2
        assert sm.context.total_questions_asked == 2

    def test_record_answer(self):
        sm = InterviewStateMachine()
        sm.record_answer(1, "My name is John", 0.8)
        assert sm.context.answers[1] == "My name is John"
        assert sm.context.scores[1] == 0.8

    def test_retry_within_limit(self):
        sm = InterviewStateMachine()
        sm.record_question(1)
        assert sm.record_retry()  # First retry
        assert sm.record_retry()  # Second retry
        assert sm.context.retries_on_current_question == MAX_RETRIES_PER_QUESTION

    def test_retry_exceeds_limit(self):
        sm = InterviewStateMachine()
        sm.record_question(1)
        for _ in range(MAX_RETRIES_PER_QUESTION):
            sm.record_retry()
        assert not sm.record_retry()  # Should fail

    def test_should_advance_state_after_max_questions(self):
        sm = InterviewStateMachine()
        for i in range(MAX_QUESTIONS_PER_STATE):
            sm.record_question(i + 1)
        assert sm.should_advance_state()

    def test_should_not_advance_state_before_max(self):
        sm = InterviewStateMachine()
        sm.record_question(1)
        assert not sm.should_advance_state()

    def test_counters_reset_on_advance(self):
        sm = InterviewStateMachine()
        sm.record_question(1)
        sm.record_question(2)
        sm.advance()
        assert sm.context.questions_asked_in_state == 0
        assert sm.context.retries_on_current_question == 0
        assert sm.context.current_question_id is None


class TestStateCategory:
    """Test state-to-category mapping."""

    def test_greeting_maps_to_background(self):
        sm = InterviewStateMachine()
        assert sm.get_state_category() == "background"

    def test_academics_maps_correctly(self):
        sm = InterviewStateMachine()
        sm.advance()
        assert sm.get_state_category() == "academics"

    def test_finance_maps_correctly(self):
        sm = InterviewStateMachine()
        sm.go_to(InterviewState.FINANCE)
        assert sm.get_state_category() == "finance"

    def test_intent_maps_correctly(self):
        sm = InterviewStateMachine()
        sm.go_to(InterviewState.INTENT)
        assert sm.get_state_category() == "intent"


class TestStateHistory:
    """Test state history tracking."""

    def test_history_records_transitions(self):
        sm = InterviewStateMachine()
        sm.advance()
        sm.advance()
        assert InterviewState.GREETING in sm.context.state_history
        assert InterviewState.ACADEMICS in sm.context.state_history

    def test_full_run_history(self):
        sm = InterviewStateMachine()
        for _ in range(7):
            sm.advance()
        assert len(sm.context.state_history) == 7


class TestConfiguration:
    """Test custom configuration."""

    def test_custom_destination(self):
        sm = InterviewStateMachine(destination_country="UK")
        assert sm.context.destination_country == "UK"

    def test_custom_origin(self):
        sm = InterviewStateMachine(origin_country="Pakistan")
        assert sm.context.origin_country == "Pakistan"
