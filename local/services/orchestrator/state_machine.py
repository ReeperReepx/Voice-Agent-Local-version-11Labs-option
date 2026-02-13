"""Deterministic interview state machine.

States: greeting → academics → course_choice → finance → intent → country_specific → summary
No LLM decides state transitions — all transitions are rule-based.
"""

from __future__ import annotations

from enum import Enum
from dataclasses import dataclass, field
from typing import Optional


class InterviewState(Enum):
    GREETING = "greeting"
    ACADEMICS = "academics"
    COURSE_CHOICE = "course_choice"
    FINANCE = "finance"
    INTENT = "intent"
    COUNTRY_SPECIFIC = "country_specific"
    SUMMARY = "summary"
    ENDED = "ended"


# Valid state transitions (deterministic order)
TRANSITIONS: dict[InterviewState, InterviewState] = {
    InterviewState.GREETING: InterviewState.ACADEMICS,
    InterviewState.ACADEMICS: InterviewState.COURSE_CHOICE,
    InterviewState.COURSE_CHOICE: InterviewState.FINANCE,
    InterviewState.FINANCE: InterviewState.INTENT,
    InterviewState.INTENT: InterviewState.COUNTRY_SPECIFIC,
    InterviewState.COUNTRY_SPECIFIC: InterviewState.SUMMARY,
    InterviewState.SUMMARY: InterviewState.ENDED,
}

# Max retries per question before moving on
MAX_RETRIES_PER_QUESTION = 2
# Max questions per state before advancing
MAX_QUESTIONS_PER_STATE = 4


@dataclass
class StateContext:
    """Context maintained across the interview."""
    destination_country: str = "US"
    origin_country: str = "India"
    current_state: InterviewState = InterviewState.GREETING
    questions_asked_in_state: int = 0
    retries_on_current_question: int = 0
    current_question_id: Optional[int] = None
    answers: dict = field(default_factory=dict)  # question_id -> answer text
    scores: dict = field(default_factory=dict)  # question_id -> score
    state_history: list = field(default_factory=list)
    total_questions_asked: int = 0

    def reset_state_counters(self):
        self.questions_asked_in_state = 0
        self.retries_on_current_question = 0
        self.current_question_id = None


class InterviewStateMachine:
    """Deterministic state machine for visa interview flow."""

    def __init__(self, destination_country: str = "US", origin_country: str = "India"):
        self.context = StateContext(
            destination_country=destination_country,
            origin_country=origin_country,
        )

    @property
    def current_state(self) -> InterviewState:
        return self.context.current_state

    @property
    def is_ended(self) -> bool:
        return self.context.current_state == InterviewState.ENDED

    def advance(self) -> InterviewState:
        """Advance to the next state. Raises if no valid transition exists."""
        current = self.context.current_state
        if current not in TRANSITIONS:
            raise InvalidTransitionError(
                f"Cannot advance from {current.value} — no valid transition"
            )
        next_state = TRANSITIONS[current]
        self.context.state_history.append(current)
        self.context.current_state = next_state
        self.context.reset_state_counters()
        return next_state

    def can_advance(self) -> bool:
        """Check if we can move to the next state."""
        return self.context.current_state in TRANSITIONS

    def record_question(self, question_id: int) -> None:
        """Record that a question was asked."""
        self.context.current_question_id = question_id
        self.context.questions_asked_in_state += 1
        self.context.total_questions_asked += 1
        self.context.retries_on_current_question = 0

    def record_answer(self, question_id: int, answer: str, score: float) -> None:
        """Record an answer and its score."""
        self.context.answers[question_id] = answer
        self.context.scores[question_id] = score

    def record_retry(self) -> bool:
        """Record a retry attempt. Returns False if max retries exceeded."""
        self.context.retries_on_current_question += 1
        return self.context.retries_on_current_question <= MAX_RETRIES_PER_QUESTION

    def should_advance_state(self) -> bool:
        """Check if we should move to the next state based on questions asked."""
        return self.context.questions_asked_in_state >= MAX_QUESTIONS_PER_STATE

    def get_state_category(self) -> str:
        """Map current state to visa_questions category for DB lookup."""
        state_to_category = {
            InterviewState.GREETING: "background",
            InterviewState.ACADEMICS: "academics",
            InterviewState.COURSE_CHOICE: "course_choice",
            InterviewState.FINANCE: "finance",
            InterviewState.INTENT: "intent",
            InterviewState.COUNTRY_SPECIFIC: "country_specific",
            InterviewState.SUMMARY: "background",
        }
        return state_to_category.get(self.context.current_state, "background")

    def go_to(self, state: InterviewState) -> None:
        """Jump to a specific state (only for valid transitions or same state)."""
        if state == self.context.current_state:
            return
        # Only allow forward transitions
        current = self.context.current_state
        reachable = current
        while reachable in TRANSITIONS:
            reachable = TRANSITIONS[reachable]
            if reachable == state:
                self.context.state_history.append(current)
                self.context.current_state = state
                self.context.reset_state_counters()
                return
        raise InvalidTransitionError(
            f"Cannot jump from {current.value} to {state.value} — not reachable"
        )


class InvalidTransitionError(Exception):
    """Raised when an invalid state transition is attempted."""
    pass
