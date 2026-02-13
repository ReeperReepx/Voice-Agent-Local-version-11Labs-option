# Phase 4: ASR — Pingala V1

## Task
Streaming speech-to-text for English, Hindi, and Hinglish using Pingala V1.

## Requirements
- `services/asr/pingala/model_loader.py` — load Pingala V1 model
- `services/asr/pingala/streaming_asr.py` — streaming transcription with partial transcripts
- `services/asr/pingala/lang_detection.py` — detect language from first 1-2 seconds
- No fallback (Vakyansh excluded)

## Completion Criteria (tests must pass)
- `pytest tests/unit/test_asr.py` — model loads, transcribes test audio
- `pytest tests/integration/test_asr_orchestrator.py` — ASR output feeds into language control + orchestrator
- Partial transcripts available during speech
- Mixed Hindi/English input handled
- `<promise>COMPLETE</promise>`
