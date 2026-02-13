# Phase 3: LLM Integration (Qwen2.5-72B)

## Task
Wire up Qwen2.5-72B-Instruct for examiner-style response generation.

## Requirements
- `services/llm/qwen_runtime.py` — connect to local Qwen2.5 (via vLLM OpenAI-compatible API or Ollama)
- `services/llm/prompt_templates/` — base_system.txt, examiner_tone.txt, explanation_mode.txt
- `services/llm/response_validator.py` — reject scripted answers, hallucinated facts, immigration advice

## Completion Criteria (tests must pass)
- `pytest tests/unit/test_response_validator.py` — blocks scripted answers, blocks legal advice, blocks hallucinations
- `pytest tests/integration/test_orchestrator_llm.py` — orchestrator sends context, LLM returns valid examiner response
- LLM respects input_language = output_language rule
- `<promise>COMPLETE</promise>`
