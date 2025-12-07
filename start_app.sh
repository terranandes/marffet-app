#!/bin/bash

# Kill any existing processes on port 8000 (Backend)
fuser -k 8000/tcp || true

echo "🚀 Starting Martian Investment System..."

# Start Backend
echo "Starting FastAPI Backend..."
source .venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!

# Start Frontend
echo "Starting React Frontend..."
cd frontend
npm run dev &
FRONTEND_PID=$!

# Cleanup on exit
trap "kill $BACKEND_PID $FRONTEND_PID; exit" SIGINT SIGTERM

# Wait
wait
