# Phase 5: TTS — English + Hindi

## Task
Text-to-speech output in both languages.

## Requirements
- `services/tts/english/qwen3_tts.py` — Qwen3-TTS for English, streaming audio
- `services/tts/hindi/parler_tts.py` — Indic-finetuned Parler-TTS for Hindi, streaming audio

## Completion Criteria (tests must pass)
- `pytest tests/unit/test_tts_english.py` — generates English audio from text
- `pytest tests/unit/test_tts_hindi.py` — generates Hindi audio from text
- `pytest tests/integration/test_llm_tts.py` — correct language TTS selected based on output language
- Streaming audio output works
- `<promise>COMPLETE</promise>`
