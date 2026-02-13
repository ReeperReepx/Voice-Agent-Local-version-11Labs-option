# Task: Bilingual Language Switching

You are building the VisaWire Voice Agent.

## Current Task
Implement bilingual Hindi/English language switching in the agent behavior.

## Requirements
1. Agent asks questions in English by default
2. Detects confusion signals: "Hindi mein samjhao", "I don't understand", off-topic answers, silence
3. Switches to Hindi to explain the question simply
4. Re-asks the same question in English after Hindi explanation
5. Logs all language switches with question ID and reason

## Completion Criteria
- System prompt includes clear switching rules
- SessionLog tracks language switches correctly
- `python -m pytest server/tests/test_agent.py -v` — all tests pass
- `python -m pytest server/tests/test_feedback.py::test_language_switches_tracked -v` — passes

## Instructions
Work on ONE issue at a time. Fix errors, re-run checks. Commit when passing.

When ALL criteria are met, output:
<promise>COMPLETE</promise>
