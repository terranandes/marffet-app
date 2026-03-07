#!/bin/bash
fuser -k 3001/tcp 8001/tcp 2>/dev/null
cd .worktrees/CV_full-test-local || exit 1
uv run uvicorn app.main:app --port 8001 > backend_test.log 2>&1 &
PID_BE=$!
cd frontend
PORT=3001 bun run start > frontend_test.log 2>&1 &
PID_FE=$!
echo "Waiting 10 seconds for servers to start..."
sleep 10
cd ..
echo "Running E2E tests..."
TARGET_URL=http://localhost:3001 uv run python tests/e2e/e2e_suite.py
TEST_CODE=$?
echo "Tests finished with exit code $TEST_CODE"
kill -9 $PID_BE $PID_FE 2>/dev/null || true
fuser -k 3001/tcp 8001/tcp 2>/dev/null
exit $TEST_CODE
