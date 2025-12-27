#!/bin/bash

# Kill any existing processes on port 8000 (Backend) and 3000 (Frontend)
fuser -k 8000/tcp || true
fuser -k 3000/tcp || true

echo "🚀 Starting Martian Investment System..."

# --- 1. Backend Setup ---
if [ ! -d ".venv" ]; then
    echo "📦 Creating Python Virtual Environment..."
    python3 -m venv .venv
fi

source .venv/bin/activate

# Check if packages are installed (check for plotly to ensure full set)
if ! pip show plotly &> /dev/null; then
    echo "📦 Installing Backend Dependencies..."
    pip install fastapi uvicorn httpx pandas numpy openpyxl plotly
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
echo "Starting Next.js Frontend..."
# Note: Host is bound via package.json script "dev"
npm run dev &
FRONTEND_PID=$!

# Cleanup on exit
trap "kill $BACKEND_PID $FRONTEND_PID; exit" SIGINT SIGTERM

# Wait
wait
