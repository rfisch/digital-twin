#!/bin/bash
# Runs the wake server (Python) + Caddy (HTTPS proxy) together.
# Managed by launchd via com.jacq.wake.plist.
set -e

PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
LOG_DIR="$PROJECT_DIR/logs"
mkdir -p "$LOG_DIR"

cleanup() {
    kill "$WAKE_PID" 2>/dev/null
    /opt/homebrew/bin/caddy stop 2>/dev/null
    wait
}
trap cleanup EXIT INT TERM

# Start wake server
"$PROJECT_DIR/.venv/bin/python" "$PROJECT_DIR/scripts/wake_server.py" >> "$LOG_DIR/wake-server.log" 2>&1 &
WAKE_PID=$!

# Start Caddy (blocks until signal)
exec /opt/homebrew/bin/caddy run --config "$PROJECT_DIR/Caddyfile" 2>> "$LOG_DIR/caddy.log"
