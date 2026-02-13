# Phase 2: Interview Orchestrator (State Machine)

## Task
Build a deterministic state machine that drives the interview. No LLM decides state transitions.

## Requirements
- `services/orchestrator/state_machine.py` — states: greeting → academics → course_choice → finance → intent → country_specific → summary
- `services/orchestrator/interview_states/` — one file per state with entry/exit logic, question selection, retry rules
- `services/orchestrator/language_control.py` — primary_language, explanation_mode, auto-reversion
- `services/orchestrator/scoring.py` — per-question scoring, contradiction tracking
- `services/orchestrator/contradiction_tracker.py` — flag inconsistencies across answers

## Completion Criteria (tests must pass)
- `pytest tests/unit/test_state_machine.py` — all transitions valid, invalid blocked
- `pytest tests/unit/test_language_control.py` — switch only on explicit request, auto-revert works
- `pytest tests/unit/test_scoring.py` — scores update, contradictions detected
- State machine advances through all 7 states in a mock run
- `<promise>COMPLETE</promise>`
