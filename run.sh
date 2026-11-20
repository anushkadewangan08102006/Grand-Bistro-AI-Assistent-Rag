#!/usr/bin/env bash
# Startup script for Le Grand Bistro Culinary Operations Assistant
set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

echo "========================================================================"
echo "Starting Le Grand Bistro AI Culinary Operations Assistant (RAG System)"
echo "========================================================================"

# Check if port 8000 is open or in use
if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null ; then
    echo "Server already running on http://127.0.0.1:8000"
else
    echo "Starting FastAPI backend server with static frontend build on port 8000..."
    python3 -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 &
    SERVER_PID=$!
    echo "Server PID: $SERVER_PID"
    sleep 3
fi

echo ""
echo "🚀 Application available at: http://127.0.0.1:8000"
echo "📖 Swagger API documentation: http://127.0.0.1:8000/docs"
echo "🏆 Assessment Benchmark: http://127.0.0.1:8000/api/benchmark"
echo "========================================================================"
