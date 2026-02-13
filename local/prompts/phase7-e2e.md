# Phase 7: Web UI + End-to-End

## Task
Frontend adapted from existing version, full voice-to-voice loop.

## Requirements
- `web/index.html` — adapted from existing UI (WebSocket audio instead of ElevenLabs)
- Session summary / final report display
- Timer, transcript display, status indicators

## Completion Criteria (tests must pass)
- `pytest tests/e2e/test_full_interview.py` — full English interview completes (simulated audio)
- `pytest tests/e2e/test_hindi_switch.py` — explanation mode triggers and reverts
- UI loads, connects, shows transcript, shows final report
- 15-25 minute session is stable
- `<promise>COMPLETE</promise>`
