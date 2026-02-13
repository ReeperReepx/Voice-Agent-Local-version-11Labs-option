# Task: Visa Question Bank + Interview Flow

You are building the VisaWire Voice Agent.

## Current Task
Ensure the 5 core visa questions are structured correctly and injected into the agent prompt.

## Requirements
1. All 5 questions have English text, Hindi hint, category, and follow-ups
2. Questions cover: study plans, financial, return intent, academic, English proficiency
3. System prompt includes all questions formatted for the agent
4. Agent follows question order and asks follow-ups

## Completion Criteria
- `python -m pytest server/tests/test_questions.py -v` — all tests pass
- `python -m pytest server/tests/test_agent.py::test_system_prompt_contains_questions -v` — passes

## Instructions
Work on ONE issue at a time. Fix errors, re-run checks. Commit when passing.

When ALL criteria are met, output:
<promise>COMPLETE</promise>
