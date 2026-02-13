# Task: Project Scaffold + Web UI

You are building the VisaWire Voice Agent — an AI visa interview coach.

## Current Task
Verify the project scaffold works: server starts, web UI loads, all dependencies install.

## Requirements
1. `pip install -r requirements.txt` succeeds
2. `python -m uvicorn server.app:app` starts without errors
3. Hitting `http://localhost:8000/` returns the web UI HTML
4. Start and Stop buttons render correctly

## Completion Criteria
- All requirements above pass
- `python -m pytest server/tests/test_api.py::test_root_serves_html -v` passes

## Instructions
Work on ONE issue at a time. Fix errors, re-run checks. Commit when passing.

When ALL criteria are met, output:
<promise>COMPLETE</promise>
