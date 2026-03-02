#!/bin/bash
# Start FastAPI + Next.js dev servers
set -e

cd "$(dirname "$0")/.."

source .venv/bin/activate

echo "Starting FastAPI on port 8000..."
uvicorn api.main:app --reload --port 8000 &
API_PID=$!

echo "Starting Next.js on port 7860..."
cd web && npm run dev &
WEB_PID=$!

cd ..

trap "kill $API_PID $WEB_PID 2>/dev/null; exit" INT TERM

echo ""
echo "API: http://localhost:8000"
echo "Web: http://localhost:7860"
echo "Press Ctrl+C to stop"
echo ""

wait
