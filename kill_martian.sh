#!/bin/bash
echo "Stopping Martian System..."
# Kill processes on port 8000 (Backend)
fuser -k 8000/tcp 2>/dev/null
# Kill processes on port 3000 (Next.js Frontend)
fuser -k 3000/tcp 2>/dev/null
# Kill processes on port 5173/5174 (Vite Frontend - legacy)
fuser -k 5173/tcp 2>/dev/null
fuser -k 5174/tcp 2>/dev/null
# Kill python uvicorn
pkill -f "uvicorn"
# Kill vite
pkill -f "vite"
# Kill Next.js
pkill -f "next-server"

echo "Cleanup complete. Ports 8000, 3000, 5173, 5174 should be free."
