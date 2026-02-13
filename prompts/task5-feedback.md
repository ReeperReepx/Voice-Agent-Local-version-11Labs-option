# Task: Session Feedback Summary

You are building the VisaWire Voice Agent.

## Current Task
Generate a post-session feedback report with scores and improvement areas.

## Requirements
1. Feedback includes: session duration, questions faced, English proficiency rating
2. Tracks English vs Hindi response ratio
3. Lists questions that needed Hindi help (by category name)
4. Provides actionable improvement suggestions
5. Human-readable summary text

## Completion Criteria
- `python -m pytest server/tests/test_feedback.py -v` — all 6 tests pass
- `python -m pytest server/tests/test_api.py::test_end_session_returns_feedback -v` — passes
- Feedback summary includes: duration, proficiency, switch count, improvements

## Instructions
Work on ONE issue at a time. Fix errors, re-run checks. Commit when passing.

When ALL criteria are met, output:
<promise>COMPLETE</promise>
