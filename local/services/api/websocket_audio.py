"""WebSocket audio streaming endpoint.

Bidirectional audio: mic in -> ASR -> orchestrator -> LLM -> TTS -> speaker out.

Connection states: IDLE -> LISTENING -> PROCESSING -> SPEAKING -> IDLE

Protocol (client -> server):
  JSON  {"type": "speech_start"}           — user started speaking
  JSON  {"type": "speech_end"}             — user stopped speaking
  JSON  {"type": "text_input", "text": ""} — text fallback (no mic)
  JSON  {"type": "end_session"}            — close session
  binary  raw PCM16 frames (16kHz mono)    — audio from mic

Protocol (server -> client):
  JSON  {"type": "transcript_partial", "text": "..."}
  JSON  {"type": "transcript_final", "text": "...", "language": "en"}
  JSON  {"type": "agent_thinking"}
  JSON  {"type": "agent_response", "text": "...", "state": "...", "score": 0.8}
  JSON  {"type": "tts_start"}
  JSON  {"type": "tts_end"}
  JSON  {"type": "state_change", "state": "..."}
  JSON  {"type": "error", "message": "..."}
  JSON  {"type": "asr_status", "ready": bool, "message": "..."}
  binary  PCM16 chunks (24kHz mono)        — TTS audio for playback
"""

import asyncio
import enum
import json
import logging
import traceback

from fastapi import WebSocket, WebSocketDisconnect

from services.session.session_manager import SessionManager
from services.session.audit_log import get_audit_logger
from services.asr.pingala.streaming_asr import StreamingASR
from services.orchestrator.chat_pipeline import process_chat_turn
from services.audio_pipeline import (
    pcm16_to_float32,
    synthesize_and_normalize,
    chunk_pcm_bytes,
)

logger = logging.getLogger(__name__)


class ConnectionState(enum.Enum):
    IDLE = "idle"
    LISTENING = "listening"
    PROCESSING = "processing"
    SPEAKING = "speaking"


async def _safe_send_json(ws: WebSocket, data: dict) -> bool:
    """Send JSON, returning False if the connection is gone."""
    try:
        await ws.send_json(data)
        return True
    except Exception:
        return False


async def _safe_send_bytes(ws: WebSocket, data: bytes) -> bool:
    """Send bytes, returning False if the connection is gone."""
    try:
        await ws.send_bytes(data)
        return True
    except Exception:
        return False


async def audio_websocket(
    websocket: WebSocket,
    session_id: str,
    session_manager: SessionManager,
):
    """Handle bidirectional audio WebSocket connection."""
    await websocket.accept()
    logger.info("[WS:%s] Connection accepted", session_id)

    session = session_manager.get_session(session_id)
    if not session:
        logger.warning("[WS:%s] Session not found", session_id)
        await _safe_send_json(websocket, {"type": "error", "message": "Session not found"})
        try:
            await websocket.close()
        except Exception:
            pass
        return

    audit = get_audit_logger()
    state = ConnectionState.IDLE
    asr = StreamingASR()
    asr_ready = False
    speaking_cancelled = False

    # Start ASR init in the background — don't block the WebSocket
    async def _init_asr():
        nonlocal asr_ready
        try:
            logger.info("[WS:%s] Loading ASR model...", session_id)
            await asyncio.to_thread(asr.initialize)
            asr_ready = True
            logger.info("[WS:%s] ASR ready", session_id)
            await _safe_send_json(websocket, {
                "type": "asr_status",
                "ready": True,
                "message": "Voice recognition ready",
            })
        except Exception as e:
            logger.warning("[WS:%s] ASR init failed: %s", session_id, e)
            await _safe_send_json(websocket, {
                "type": "asr_status",
                "ready": False,
                "message": "Voice recognition unavailable — type your answers below",
            })

    asr_task = asyncio.create_task(_init_asr())

    # Send initial greeting immediately
    await _safe_send_json(websocket, {
        "type": "state_change",
        "state": session.state_machine.current_state.value,
        "message": "Interview session started. Please introduce yourself.",
    })

    async def _send_tts(text: str, language: str):
        """Synthesise speech and stream PCM16 chunks to the client."""
        nonlocal state, speaking_cancelled
        state = ConnectionState.SPEAKING
        speaking_cancelled = False

        logger.info("[WS:%s] TTS start — lang=%s, text=%s...", session_id, language, text[:60])
        if not await _safe_send_json(websocket, {"type": "tts_start"}):
            return

        try:
            # Run TTS in a thread, sending keepalive pings every 5s
            # to prevent the browser from closing the idle WebSocket.
            tts_future = asyncio.get_event_loop().run_in_executor(
                None, synthesize_and_normalize, text, language
            )
            while True:
                try:
                    pcm_bytes = await asyncio.wait_for(
                        asyncio.shield(tts_future), timeout=5.0
                    )
                    break  # synthesis done
                except asyncio.TimeoutError:
                    # Still synthesising — send a keepalive status
                    if not await _safe_send_json(websocket, {
                        "type": "status",
                        "message": "Generating speech...",
                    }):
                        return  # client gone

            logger.info("[WS:%s] TTS synthesized %d bytes", session_id, len(pcm_bytes))
            chunks = chunk_pcm_bytes(pcm_bytes)
            logger.info("[WS:%s] Streaming %d audio chunks", session_id, len(chunks))

            for i, chunk in enumerate(chunks):
                if speaking_cancelled:
                    logger.info("[WS:%s] TTS cancelled at chunk %d/%d", session_id, i, len(chunks))
                    break
                if not await _safe_send_bytes(websocket, chunk):
                    logger.warning("[WS:%s] Failed to send audio chunk %d", session_id, i)
                    return
                await asyncio.sleep(0.01)
        except Exception as e:
            logger.error("[WS:%s] TTS failed: %s\n%s", session_id, e, traceback.format_exc())
            await _safe_send_json(websocket, {
                "type": "error",
                "message": f"TTS failed: {e}",
            })

        await _safe_send_json(websocket, {"type": "tts_end"})
        if not speaking_cancelled:
            state = ConnectionState.IDLE
        logger.info("[WS:%s] TTS done, state=%s", session_id, state.value)

    async def _handle_final_transcript(transcript_text: str, language: str):
        """Run the chat pipeline on finalised transcript and stream TTS back."""
        nonlocal state
        state = ConnectionState.PROCESSING
        logger.info("[WS:%s] Processing transcript: %s", session_id, transcript_text[:80])

        if not await _safe_send_json(websocket, {
            "type": "transcript_final",
            "text": transcript_text,
            "language": language,
        }):
            return

        await _safe_send_json(websocket, {"type": "agent_thinking"})

        try:
            logger.info("[WS:%s] Calling LLM pipeline...", session_id)
            llm_future = asyncio.get_event_loop().run_in_executor(
                None, process_chat_turn, session, transcript_text, audit
            )
            while True:
                try:
                    result = await asyncio.wait_for(
                        asyncio.shield(llm_future), timeout=5.0
                    )
                    break
                except asyncio.TimeoutError:
                    if not await _safe_send_json(websocket, {
                        "type": "status",
                        "message": "Officer is thinking...",
                    }):
                        return
            logger.info("[WS:%s] LLM responded: %s...", session_id, result.response_text[:60])
        except Exception as e:
            logger.error("[WS:%s] Chat pipeline failed: %s\n%s", session_id, e, traceback.format_exc())
            await _safe_send_json(websocket, {
                "type": "error",
                "message": f"Pipeline error: {e}",
            })
            state = ConnectionState.IDLE
            return

        await _safe_send_json(websocket, {
            "type": "agent_response",
            "text": result.response_text,
            "state": result.current_state,
            "score": result.score,
            "explanation_mode": result.explanation_mode,
        })

        if result.current_state != session.state_machine.current_state.value:
            await _safe_send_json(websocket, {
                "type": "state_change",
                "state": result.current_state,
            })

        # Synthesise and stream TTS audio
        await _send_tts(result.response_text, result.output_language)

        # Auto-end if interview is complete
        if result.current_state == "ended":
            await _safe_send_json(websocket, {
                "type": "state_change",
                "state": "ended",
                "message": "Interview complete.",
            })

    try:
        while True:
            data = await websocket.receive()

            # Handle WebSocket disconnect message
            if data.get("type") == "websocket.disconnect":
                logger.info("[WS:%s] Client sent disconnect", session_id)
                break

            if "bytes" in data:
                if state != ConnectionState.LISTENING:
                    continue
                if not asr_ready:
                    continue

                audio_f32 = pcm16_to_float32(data["bytes"])
                try:
                    segment = await asyncio.to_thread(asr.feed_audio, audio_f32)
                except Exception as e:
                    logger.warning("[WS:%s] ASR feed error: %s", session_id, e)
                    continue

                if segment and segment.text:
                    logger.info("[WS:%s] Partial transcript: %s", session_id, segment.text)
                    await _safe_send_json(websocket, {
                        "type": "transcript_partial",
                        "text": segment.text,
                        "is_partial": True,
                    })

            elif "text" in data:
                message = json.loads(data["text"])
                msg_type = message.get("type", "")
                logger.info("[WS:%s] Received msg type=%s, state=%s, asr_ready=%s",
                            session_id, msg_type, state.value, asr_ready)

                if msg_type == "speech_start":
                    if state == ConnectionState.SPEAKING:
                        speaking_cancelled = True
                        logger.info("[WS:%s] Barge-in: cancelling TTS", session_id)

                    state = ConnectionState.LISTENING
                    if asr_ready:
                        asr.reset()

                elif msg_type == "speech_end":
                    if state != ConnectionState.LISTENING:
                        logger.info("[WS:%s] speech_end ignored — state=%s", session_id, state.value)
                        continue

                    if not asr_ready:
                        logger.warning("[WS:%s] speech_end but ASR not ready", session_id)
                        await _safe_send_json(websocket, {
                            "type": "error",
                            "message": "Voice recognition not available. Please type your answer below.",
                        })
                        state = ConnectionState.IDLE
                        continue

                    try:
                        final_seg = await asyncio.to_thread(asr.finalize)
                    except Exception as e:
                        logger.warning("[WS:%s] ASR finalize error: %s", session_id, e)
                        state = ConnectionState.IDLE
                        continue

                    full_text = asr.get_full_transcript().strip()
                    if final_seg and final_seg.text:
                        full_text = (full_text + " " + final_seg.text).strip()

                    logger.info("[WS:%s] Final transcript: '%s'", session_id, full_text)

                    # Ignore empty or very short transcripts (noise, "mm-hmm", etc.)
                    word_count = len(full_text.split())
                    if not full_text or word_count < 2:
                        logger.info("[WS:%s] Transcript too short (%d words) — ignoring", session_id, word_count)
                        state = ConnectionState.IDLE
                        if full_text:
                            await _safe_send_json(websocket, {
                                "type": "error",
                                "message": f"Too short: \"{full_text}\" — please say more.",
                            })
                        else:
                            await _safe_send_json(websocket, {
                                "type": "error",
                                "message": "Could not hear you. Please try again or type your answer.",
                            })
                        continue

                    lang = final_seg.language if final_seg else "en"
                    await _handle_final_transcript(full_text, lang)

                elif msg_type == "text_input":
                    text = message.get("text", "").strip()
                    if not text:
                        continue
                    lang = message.get("language", "en")
                    logger.info("[WS:%s] Text input: %s", session_id, text[:80])
                    await _handle_final_transcript(text, lang)

                elif msg_type == "end_session":
                    logger.info("[WS:%s] Client requested end_session", session_id)
                    break

    except WebSocketDisconnect:
        logger.info("[WS:%s] WebSocket disconnected", session_id)
    except Exception as e:
        logger.error("[WS:%s] WebSocket error: %s\n%s", session_id, e, traceback.format_exc())
    finally:
        asr_task.cancel()
        try:
            await websocket.close()
        except Exception:
            pass
        logger.info("[WS:%s] Connection closed", session_id)
