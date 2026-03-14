#!/bin/bash
cd .worktrees/phase-36-mobile

# Start backend
source .venv/bin/activate
cd backend
python3 -m pip install -r requirements.txt &> /dev/null
export TESTING=true
uvicorn main:app --port 8001 &
BACKEND_PID=$!
cd ..

# Start frontend
cd frontend
bun install &> /dev/null
bun run dev --port 3001 &
FRONTEND_PID=$!
cd ..

# Wait for services
echo "Waiting for services..."
sleep 15

# Run the UI test
python3 -m pytest tests/e2e/test_mobile_ux.py -v

# Cleanup
kill $BACKEND_PID
kill $FRONTEND_PID
