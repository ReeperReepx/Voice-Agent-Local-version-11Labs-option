"""ElevenLabs Conversational AI agent integration."""

from __future__ import annotations

import os
import time
from dataclasses import dataclass, field

from dotenv import load_dotenv

from server.questions import get_all_questions

load_dotenv()

SYSTEM_PROMPT = """You are a visa interview officer conducting a mock student visa interview.

BEHAVIOR:
- Be professional, neutral, and realistic — like a real visa officer.
- Ask questions in English by default.
- If the student shows confusion (says "Hindi mein samjhao", "I don't understand", gives an off-topic answer, or stays silent for too long), switch to Hindi to explain the question simply, then re-ask in English.
- After a Hindi explanation, say something like: "Let me ask that again in English..." and re-ask.
- Encourage the student to answer in English, but accept Hindi answers (note it internally).
- Ask follow-up questions when answers are vague or incomplete.
- Keep track of which questions needed Hindi help.

QUESTIONS TO ASK (in order):
{questions}

FLOW:
1. Greet the student and introduce yourself as the visa officer.
2. Ask each question, listen to the response, ask follow-ups if needed.
3. After all questions, thank the student and end the interview.
4. Summarize how they did.

LANGUAGE SWITCHING RULES:
- Default: English
- Switch trigger: student confusion, explicit Hindi request, silence, off-topic response
- After Hindi help: always re-ask the same question in English
- Track every language switch with the question ID
"""


@dataclass
class SessionLog:
    """Tracks a single interview session."""
    session_id: str
    start_time: float = field(default_factory=time.time)
    end_time: float | None = None
    questions_asked: list = field(default_factory=list)
    language_switches: list = field(default_factory=list)
    transcript: list = field(default_factory=list)
    student_language_usage: dict = field(default_factory=lambda: {"english": 0, "hindi": 0})

    def add_message(self, role: str, text: str, language: str = "en"):
        self.transcript.append({
            "role": role,
            "text": text,
            "language": language,
            "timestamp": time.time(),
        })
        if role == "student":
            if language == "hi":
                self.student_language_usage["hindi"] += 1
            else:
                self.student_language_usage["english"] += 1

    def add_language_switch(self, question_id: int, reason: str):
        self.language_switches.append({
            "question_id": question_id,
            "reason": reason,
            "timestamp": time.time(),
        })

    def end_session(self):
        self.end_time = time.time()

    def duration_minutes(self) -> float:
        end = self.end_time or time.time()
        return round((end - self.start_time) / 60, 1)

    def to_dict(self) -> dict:
        return {
            "session_id": self.session_id,
            "duration_minutes": self.duration_minutes(),
            "questions_asked": self.questions_asked,
            "language_switches": self.language_switches,
            "transcript": self.transcript,
            "student_language_usage": self.student_language_usage,
        }


def build_system_prompt() -> str:
    """Build the system prompt with all questions injected."""
    questions = get_all_questions()
    questions_text = ""
    for q in questions:
        questions_text += f"\n{q['id']}. {q['question_en']}"
        questions_text += f"\n   Hindi hint: {q['hint_hi']}"
        for fu in q["follow_ups"]:
            questions_text += f"\n   - Follow-up: {fu}"
        questions_text += "\n"
    return SYSTEM_PROMPT.format(questions=questions_text)


def get_signed_url() -> str:
    """Get a signed URL for a conversational AI session via REST API."""
    import httpx

    api_key = os.getenv("ELEVENLABS_API_KEY")
    agent_id = os.getenv("ELEVENLABS_AGENT_ID")
    if not api_key:
        raise ValueError("ELEVENLABS_API_KEY not set in environment")
    if not agent_id:
        raise ValueError("ELEVENLABS_AGENT_ID not set in environment")

    response = httpx.get(
        f"https://api.elevenlabs.io/v1/convai/conversation/get-signed-url?agent_id={agent_id}",
        headers={"xi-api-key": api_key},
    )
    response.raise_for_status()
    return response.json()["signed_url"]
