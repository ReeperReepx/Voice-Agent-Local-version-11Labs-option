"""Session lifecycle manager.

Manages interview session creation, state tracking, and finalization.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Optional

from services.orchestrator.state_machine import InterviewStateMachine
from services.orchestrator.language_control import LanguageController, Language
from services.orchestrator.scoring import InterviewScorer
from services.orchestrator.contradiction_tracker import ContradictionTracker


@dataclass
class Session:
    """A single interview session."""
    session_id: str
    destination_country: str
    origin_country: str
    created_at: float = field(default_factory=time.time)
    ended_at: Optional[float] = None
    state_machine: InterviewStateMachine = field(default=None)
    language_controller: LanguageController = field(default=None)
    scorer: InterviewScorer = field(default_factory=InterviewScorer)
    contradiction_tracker: ContradictionTracker = field(default_factory=ContradictionTracker)
    transcript: list = field(default_factory=list)
    is_active: bool = True

    def __post_init__(self):
        if self.state_machine is None:
            self.state_machine = InterviewStateMachine(
                destination_country=self.destination_country,
                origin_country=self.origin_country,
            )
        if self.language_controller is None:
            self.language_controller = LanguageController()

    def duration_minutes(self) -> float:
        end = self.ended_at or time.time()
        return round((end - self.created_at) / 60, 1)

    def add_transcript_entry(self, role: str, text: str, language: str = "en"):
        self.transcript.append({
            "role": role,
            "text": text,
            "language": language,
            "timestamp": time.time(),
        })

    def end(self):
        self.ended_at = time.time()
        self.is_active = False

    def to_dict(self) -> dict:
        return {
            "session_id": self.session_id,
            "destination_country": self.destination_country,
            "origin_country": self.origin_country,
            "duration_minutes": self.duration_minutes(),
            "current_state": self.state_machine.current_state.value,
            "is_active": self.is_active,
            "total_questions": self.state_machine.context.total_questions_asked,
            "transcript_length": len(self.transcript),
        }


class SessionManager:
    """Manages all interview sessions."""

    def __init__(self):
        self._sessions: dict[str, Session] = {}

    def create_session(
        self,
        destination_country: str = "US",
        origin_country: str = "India",
    ) -> Session:
        session_id = str(uuid.uuid4())[:8]
        session = Session(
            session_id=session_id,
            destination_country=destination_country,
            origin_country=origin_country,
        )
        self._sessions[session_id] = session
        return session

    def get_session(self, session_id: str) -> Optional[Session]:
        return self._sessions.get(session_id)

    def end_session(self, session_id: str) -> Optional[dict]:
        session = self._sessions.get(session_id)
        if not session:
            return None
        session.end()
        report = session.scorer.generate_report()
        report["session_id"] = session_id
        report["duration_minutes"] = session.duration_minutes()
        report["language_switches"] = session.language_controller.state.switch_count
        report["contradictions_found"] = len(session.contradiction_tracker.get_all_contradictions())
        return report

    def get_active_sessions(self) -> list[Session]:
        return [s for s in self._sessions.values() if s.is_active]

    def session_count(self) -> int:
        return len(self._sessions)
