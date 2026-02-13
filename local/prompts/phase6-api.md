# Phase 6: API + WebSocket Audio Layer

## Task
Wire everything together with HTTP + WebSocket endpoints.

## Requirements
- `services/api/http_gateway.py` — FastAPI server: session start/end, question retrieval, feedback
- `services/api/websocket_audio.py` — WebSocket for bidirectional audio streaming
- `services/session/session_manager.py` — session lifecycle
- `services/session/redis_store.py` — Redis state storage

## Completion Criteria (tests must pass)
- `pytest tests/integration/test_api.py` — all endpoints return correct responses
- WebSocket accepts audio, returns audio
- Full data flow: audio → ASR → orchestrator → DB → LLM → validator → TTS → audio
- `<promise>COMPLETE</promise>`
