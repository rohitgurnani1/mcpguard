#!/usr/bin/env bash
# Start MCPGuard backend + frontend together for local development.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

if [[ ! -d ".venv" ]]; then
  echo "Missing .venv — run: make install"
  exit 1
fi

if [[ ! -d "frontend/node_modules" ]]; then
  echo "Missing frontend deps — run: make install"
  exit 1
fi

cleanup() {
  echo ""
  echo "Shutting down MCPGuard dev servers..."
  for pid in $(jobs -p); do
    kill "$pid" 2>/dev/null || true
  done
  wait 2>/dev/null || true
}
trap cleanup EXIT INT TERM

echo "Starting MCPGuard backend on http://localhost:8000"
source .venv/bin/activate
uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000 &

echo "Starting MCPGuard frontend on http://localhost:5173"
(cd frontend && npm run dev -- --host 127.0.0.1) &

echo ""
echo "MCPGuard is running:"
echo "  Dashboard  → http://localhost:5173"
echo "  API docs   → http://localhost:8000/docs"
echo "  Press Ctrl+C to stop both"
echo ""

wait
