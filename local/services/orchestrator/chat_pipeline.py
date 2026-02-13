"""Reusable chat pipeline for both HTTP and WebSocket handlers.

Extracts the shared logic: language control, LLM call, validation, scoring,
state advancement. Both /chat endpoint and WebSocket handler call this.
"""

import logging
from dataclasses import dataclass

from services.session.session_manager import Session
from services.session.audit_log import AuditLogger
from services.llm.qwen_runtime import build_system_prompt, generate_response
from services.llm.response_validator import validate_response, get_safe_fallback

logger = logging.getLogger(__name__)


@dataclass
class ChatResult:
    """Result of a single chat turn through the pipeline."""
    response_text: str
    current_state: str
    explanation_mode: bool
    score: float
    output_language: str


def process_chat_turn(session: Session, user_text: str, audit: AuditLogger) -> ChatResult:
    """Run one user turn through the full interview pipeline.

    Synchronous — call via asyncio.to_thread() from async handlers.

    Args:
        session: Active interview session.
        user_text: The student's message text.
        audit: Audit logger instance.

    Returns:
        ChatResult with the agent response and updated state info.
    """
    # Log user message
    session.add_transcript_entry("student", user_text)

    # Language control
    lc_result = session.language_controller.process_input(user_text)

    # Build conversation history from transcript
    history = []
    for entry in session.transcript[:-1]:  # exclude the message we just added
        role = "assistant" if entry["role"] == "agent" else "user"
        history.append({"role": role, "content": entry["text"]})

    # Build system prompt from current state
    current_state = session.state_machine.current_state.value
    system_prompt = build_system_prompt(
        state=current_state,
        destination_country=session.destination_country,
        explanation_mode=lc_result["explanation_mode"],
    )

    # Call LLM
    try:
        response_text = generate_response(
            system_prompt=system_prompt,
            conversation_history=history[-10:],
            user_message=user_text,
            language=lc_result["output_language"].value,
        )
    except Exception as e:
        logger.warning("LLM call failed: %s", e)
        response_text = (
            "I see. Could you tell me more about that? "
            "What specific details can you share?"
        )

    # Validate response
    validation = validate_response(response_text)
    if not validation.is_valid:
        response_text = get_safe_fallback(validation.blocked_category)

    # Log agent response
    session.add_transcript_entry("agent", response_text)

    # Score the answer (simple heuristic)
    words = user_text.split()
    score = min(1.0, len(words) / 20.0) * 0.7 + 0.3
    q_id = session.state_machine.context.total_questions_asked + 1
    category = current_state
    session.scorer.record_score(q_id, score, category=category)
    session.state_machine.record_answer(q_id, user_text, score)

    # Audit log
    audit.log_answer(
        session.session_id,
        question_id=q_id,
        answer=user_text,
        score=score,
        category=category,
    )

    # Auto-advance state if enough questions answered
    new_state = current_state
    if session.state_machine.should_advance_state() and session.state_machine.can_advance():
        new_state = session.state_machine.advance().value

    output_language = lc_result["output_language"].value

    return ChatResult(
        response_text=response_text,
        current_state=new_state,
        explanation_mode=lc_result["explanation_mode"],
        score=round(score, 2),
        output_language=output_language,
    )
