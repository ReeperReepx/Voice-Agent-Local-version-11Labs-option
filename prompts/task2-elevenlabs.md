# Task: ElevenLabs Conversational AI Integration

You are building the VisaWire Voice Agent.

## Current Task
Wire up ElevenLabs Conversational AI so clicking "Start Interview" opens a live voice session.

## Requirements
1. `/api/session/start` returns a valid signed URL from ElevenLabs
2. Web UI connects to the signed URL and starts a voice conversation
3. Session ID is tracked server-side
4. Agent uses the visa officer system prompt with all 5 questions

## Completion Criteria
- `python -m pytest server/tests/test_api.py -v` — all tests pass
- `python -m pytest server/tests/test_agent.py -v` — all tests pass
- Manual test: start session returns signed_url and system_prompt

## Instructions
Work on ONE issue at a time. Fix errors, re-run checks. Commit when passing.

When ALL criteria are met, output:
<promise>COMPLETE</promise>
