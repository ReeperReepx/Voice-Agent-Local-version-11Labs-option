"""FastAPI HTTP gateway for the local voice agent.

Endpoints: session start/end, question retrieval, feedback, chat, WebSocket audio.
"""

import asyncio
import os
import sys
import logging

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")

from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, HTTPException, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

# Add local/ to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from services.session.session_manager import SessionManager
from services.session.redis_store import RedisStore
from services.visa_db.retrieval import (
    get_questions_by_country,
    get_destinations,
    get_risk_factors,
    init_db,
    seed_db,
)
from services.llm.qwen_runtime import check_health
from services.session.audit_log import get_audit_logger
from services.orchestrator.chat_pipeline import process_chat_turn
from services.api.websocket_audio import audio_websocket

logger = logging.getLogger(__name__)

# Auto-initialize database on import
init_db()
seed_db()

app = FastAPI(title="VisaWire Local Voice Agent")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

session_manager = SessionManager()
store = RedisStore()
audit = get_audit_logger()

# Serve AudioWorklet JS and other static assets from local/web/
WEB_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "web")
app.mount("/static", StaticFiles(directory=WEB_DIR), name="static")


# --- WebSocket Route ---

@app.websocket("/ws/audio/{session_id}")
async def ws_audio(websocket: WebSocket, session_id: str):
    """Bidirectional audio WebSocket — delegates to audio_websocket handler."""
    await audio_websocket(websocket, session_id, session_manager)


# --- Request Models ---

class SessionStartRequest(BaseModel):
    destination_country: str = "US"
    origin_country: str = "India"


class MessageRequest(BaseModel):
    role: str
    text: str
    language: str = "en"


class AnswerRequest(BaseModel):
    question_id: int
    answer: str
    category: str = ""


class ChatRequest(BaseModel):
    text: str


# --- Endpoints ---

@app.get("/")
async def serve_ui():
    """Serve the web interface."""
    return FileResponse(
        os.path.join(os.path.dirname(__file__), "..", "..", "web", "index.html")
    )


@app.post("/api/session/start")
async def start_session(req: SessionStartRequest):
    """Start a new interview session."""
    session = session_manager.create_session(
        destination_country=req.destination_country,
        origin_country=req.origin_country,
    )
    # Persist to Redis
    store.set(session.session_id, session.to_dict())
    return {
        "session_id": session.session_id,
        "destination_country": session.destination_country,
        "current_state": session.state_machine.current_state.value,
    }


@app.get("/api/session/{session_id}")
async def get_session(session_id: str):
    """Get session details."""
    session = session_manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session.to_dict()


@app.post("/api/session/{session_id}/message")
async def log_message(session_id: str, req: MessageRequest):
    """Log a transcript message."""
    session = session_manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    session.add_transcript_entry(req.role, req.text, req.language)
    return {"status": "ok"}


@app.post("/api/session/{session_id}/answer")
async def process_answer(session_id: str, req: AnswerRequest):
    """Process a student's answer: score, check contradictions, decide next action."""
    session = session_manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # Language check
    lc_result = session.language_controller.process_input(req.answer, req.question_id)

    # Check contradictions
    contradictions = session.contradiction_tracker.extract_and_track(
        req.question_id, req.category, req.answer
    )

    # Simple scoring based on answer length and content
    words = req.answer.strip().split()
    score = min(1.0, len(words) / 20.0) * 0.7 + 0.3  # Base score 0.3-1.0
    if contradictions:
        score = max(0.1, score - 0.2)

    session.scorer.record_score(req.question_id, score, category=req.category)
    session.state_machine.record_answer(req.question_id, req.answer, score)

    return {
        "score": round(score, 2),
        "language_action": lc_result["action"],
        "explanation_mode": lc_result["explanation_mode"],
        "contradictions": len(contradictions),
        "should_advance": session.state_machine.should_advance_state(),
    }


@app.post("/api/session/{session_id}/chat")
async def chat(session_id: str, req: ChatRequest):
    """Send a text message and get an LLM-powered examiner response.

    Full pipeline: user text -> language control -> LLM -> validator -> scoring -> response.
    """
    session = session_manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    user_text = req.text.strip()
    if not user_text:
        raise HTTPException(status_code=400, detail="Empty message")

    result = await asyncio.to_thread(process_chat_turn, session, user_text, audit)

    return {
        "response": result.response_text,
        "current_state": result.current_state,
        "explanation_mode": result.explanation_mode,
        "score": result.score,
    }


@app.post("/api/session/{session_id}/advance")
async def advance_state(session_id: str):
    """Advance to the next interview state."""
    session = session_manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    if not session.state_machine.can_advance():
        raise HTTPException(status_code=400, detail="Cannot advance — interview ended")

    new_state = session.state_machine.advance()
    return {"new_state": new_state.value}


@app.post("/api/session/{session_id}/end")
async def end_session(session_id: str):
    """End a session and get the summary report."""
    report = session_manager.end_session(session_id)
    if not report:
        raise HTTPException(status_code=404, detail="Session not found")
    audit.log_event(session_id, "session_end", {"report_summary": {
        "average_score": report.get("average_score"),
        "readiness": report.get("readiness"),
    }})
    return report


@app.get("/api/questions/{country_code}")
async def get_questions(country_code: str, category: str = None, difficulty: int = None):
    """Get visa interview questions for a country."""
    try:
        questions = get_questions_by_country(country_code, category=category, difficulty=difficulty)
        return {"questions": questions, "count": len(questions)}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/destinations")
async def list_destinations():
    """List all supported destination countries."""
    return {"destinations": get_destinations()}


@app.get("/api/risk/{country_code}")
async def get_risk(country_code: str, origin: str = None):
    """Get risk factors for a destination."""
    try:
        risks = get_risk_factors(country_code, origin_country=origin)
        return {"risks": risks, "count": len(risks)}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "ok",
        "active_sessions": len(session_manager.get_active_sessions()),
        "redis_available": store.is_redis_available,
        "llm_available": check_health(),
    }
