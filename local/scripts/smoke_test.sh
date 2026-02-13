#!/bin/bash
# Smoke test: verify all services respond
set -e

echo "=== VisaWire Local: Smoke Test ==="

API_URL="${API_URL:-http://localhost:8000}"
PASS=0
FAIL=0

check() {
    local name="$1"
    local cmd="$2"
    echo -n "  $name... "
    if eval "$cmd" > /dev/null 2>&1; then
        echo "PASS"
        PASS=$((PASS + 1))
    else
        echo "FAIL"
        FAIL=$((FAIL + 1))
    fi
}

# 1. API health
echo ""
echo "--- API Server ---"
check "Health endpoint" "curl -sf ${API_URL}/api/health"
check "Destinations list" "curl -sf ${API_URL}/api/destinations"
check "US questions" "curl -sf ${API_URL}/api/questions/US"

# 2. Session lifecycle
echo ""
echo "--- Session Lifecycle ---"
SESSION_ID=$(curl -sf -X POST "${API_URL}/api/session/start" \
    -H 'Content-Type: application/json' \
    -d '{"destination_country":"US"}' | python3 -c "import sys,json; print(json.load(sys.stdin)['session_id'])" 2>/dev/null)

if [ -n "$SESSION_ID" ]; then
    echo "  Session created: $SESSION_ID... PASS"
    PASS=$((PASS + 1))

    check "Get session" "curl -sf ${API_URL}/api/session/${SESSION_ID}"
    check "Log message" "curl -sf -X POST ${API_URL}/api/session/${SESSION_ID}/message -H 'Content-Type: application/json' -d '{\"role\":\"student\",\"text\":\"Hello\"}'"
    check "End session" "curl -sf -X POST ${API_URL}/api/session/${SESSION_ID}/end"
else
    echo "  Session creation... FAIL"
    FAIL=$((FAIL + 1))
fi

# 3. LLM check (optional)
echo ""
echo "--- LLM Backend ---"
LLM_URL="${LLM_API_URL:-http://localhost:11434}"
check "Ollama connection" "curl -sf ${LLM_URL}/api/tags"

# 4. Database
echo ""
echo "--- Database ---"
check "Risk factors" "curl -sf '${API_URL}/api/risk/US?origin=India'"
check "UK questions" "curl -sf ${API_URL}/api/questions/UK"
check "Finance questions" "curl -sf '${API_URL}/api/questions/US?category=finance'"

# 5. Unit tests
echo ""
echo "--- Unit Tests ---"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOCAL_DIR="$(dirname "$SCRIPT_DIR")"
check "All unit tests pass" "cd '${LOCAL_DIR}' && python3 -m pytest tests/unit/ -q"

# Summary
echo ""
echo "================================"
echo "Results: $PASS passed, $FAIL failed"
echo "================================"

if [ $FAIL -gt 0 ]; then
    echo "SMOKE TEST: SOME CHECKS FAILED"
    exit 1
else
    echo "SMOKE TEST: ALL PASSED"
    exit 0
fi
