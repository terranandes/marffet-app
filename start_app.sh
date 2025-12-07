#!/bin/bash

# Kill any existing processes on port 8000 (Backend)
fuser -k 8000/tcp || true

echo "🚀 Starting Martian Investment System..."

# --- 1. Backend Setup ---
if [ ! -d ".venv" ]; then
    echo "📦 Creating Python Virtual Environment..."
    python3 -m venv .venv
fi

source .venv/bin/activate

# Check if packages are installed (simple check for fastapi)
if ! pip show fastapi &> /dev/null; then
    echo "📦 Installing Backend Dependencies..."
    pip install fastapi uvicorn httpx pandas numpy openpyxl
fi

echo "✅ Backend Ready"
echo "Starting FastAPI Backend..."
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!

# --- 2. Frontend Setup ---
cd frontend

if [ ! -d "node_modules" ]; then
    echo "📦 Installing Frontend Dependencies (this may take a minute)..."
    npm install
fi

echo "✅ Frontend Ready"
echo "Starting React Frontend..."
npm run dev -- --host &
FRONTEND_PID=$!

# Cleanup on exit
trap "kill $BACKEND_PID $FRONTEND_PID; exit" SIGINT SIGTERM

# Wait
wait
