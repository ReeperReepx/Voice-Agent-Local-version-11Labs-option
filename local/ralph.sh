#!/bin/bash
# Ralph Wiggum Loop Runner for VisaWire Local Voice Agent
# Usage: ./ralph.sh <task-name> [max-iterations]

TASK=$1
MAX=${2:-30}
ITER=0

if [ -z "$TASK" ]; then
  echo "Usage: ./ralph.sh <task-name> [max-iterations]"
  echo "Available tasks:"
  ls prompts/*.md 2>/dev/null | sed 's/prompts\//  /' | sed 's/\.md//'
  exit 1
fi

PROMPT_FILE="prompts/${TASK}.md"
if [ ! -f "$PROMPT_FILE" ]; then
  echo "Error: Prompt file not found: $PROMPT_FILE"
  exit 1
fi

echo "=== Ralph Loop: $TASK (max $MAX iterations) ==="

while [ $ITER -lt $MAX ]; do
  ITER=$((ITER + 1))
  echo ""
  echo "--- Iteration $ITER / $MAX ---"

  # Run agent with task prompt
  claude -p "$(cat $PROMPT_FILE)" > output.txt 2>&1

  # Check for completion promise
  if grep -q "<promise>COMPLETE</promise>" output.txt; then
    echo "Task '$TASK' complete in $ITER iteration(s)"
    echo "Running final verification..."
    python -m pytest tests/ -v
    exit 0
  fi

  echo "Not complete yet. Agent output tail:"
  tail -5 output.txt
done

echo ""
echo "Max iterations ($MAX) reached without completion."
exit 1
