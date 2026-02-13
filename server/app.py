"""FastAPI server for the Visa Interview Coach."""

import os
import uuid
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv

from server.agent import (
    SessionLog,
    get_signed_url,
    build_system_prompt,
)
from server.feedback import generate_feedback

load_dotenv()

app = FastAPI(title="Visa Interview Coach")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory session store (MVP — no database needed)
sessions: dict[str, SessionLog] = {}


@app.get("/")
async def serve_ui():
    """Serve the main web interface."""
    return FileResponse("web/index.html")


@app.post("/api/session/start")
async def start_session():
    """Start a new interview session. Returns agent_id (and signed_url if available)."""
    session_id = str(uuid.uuid4())[:8]
    agent_id = os.getenv("ELEVENLABS_AGENT_ID", "")

    # Try signed URL for private agents; fall back to public agent_id
    signed_url = None
    try:
        signed_url = get_signed_url()
    except Exception:
        pass

    session = SessionLog(session_id=session_id)
    sessions[session_id] = session

    return {
        "session_id": session_id,
        "agent_id": agent_id,
        "signed_url": signed_url,
        "system_prompt": build_system_prompt(),
    }


@app.post("/api/session/{session_id}/message")
async def log_message(session_id: str, role: str, text: str, language: str = "en"):
    """Log a message from the conversation transcript."""
    session = sessions.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    session.add_message(role, text, language)
    return {"status": "ok"}


@app.post("/api/session/{session_id}/switch")
async def log_language_switch(session_id: str, question_id: int, reason: str):
    """Log a language switch event."""
    session = sessions.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    session.add_language_switch(question_id, reason)
    return {"status": "ok"}


@app.post("/api/session/{session_id}/end")
async def end_session(session_id: str):
    """End a session and return feedback summary."""
    session = sessions.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    session.end_session()
    feedback = generate_feedback(session)
    return feedback


@app.get("/api/session/{session_id}")
async def get_session(session_id: str):
    """Get session details."""
    session = sessions.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session.to_dict()


# Serve static files (web UI assets)
app.mount("/static", StaticFiles(directory="web"), name="static")
