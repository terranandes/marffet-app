#!/bin/bash

# Kill any existing processes on port 8000 (Backend) and 3000 (Frontend)
fuser -k 8000/tcp || true
fuser -k 3000/tcp || true

echo "🚀 Starting Martian Investment System..."

# --- 1. Backend Setup ---

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "❌ 'uv' is not installed. Please install it: curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

echo "📦 Syncing Python Environment with uv..."
uv sync

echo "✅ Backend Ready"
echo "Starting FastAPI Backend..."
# Use uv run to execute uvicorn explicitly
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!

# --- 2. Frontend Setup ---
cd frontend

# Check if bun is installed
if ! command -v bun &> /dev/null; then
    echo "❌ 'bun' is not installed. Please install it: curl -fsSL https://bun.sh/install | bash"
    exit 1
fi

if [ ! -d "node_modules" ]; then
    echo "📦 Installing Frontend Dependencies (this may take a minute)..."
    bun install
fi

echo "✅ Frontend Ready"
echo "Starting Next.js Frontend..."
# Note: Host is bound via package.json script "dev"
bun run --bun dev &
FRONTEND_PID=$!

# Cleanup on exit
trap "kill $BACKEND_PID $FRONTEND_PID; exit" SIGINT SIGTERM

# Wait
wait
