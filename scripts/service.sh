#!/bin/bash
# Run FastAPI + Next.js as a background service (production mode, no --reload).
# Managed by launchd or manually via `make service-start / service-stop`.
set -e

# Ensure Homebrew binaries (node, npx) are on PATH when run from launchd
export PATH="/opt/homebrew/bin:$PATH"

PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
PID_DIR="$PROJECT_DIR/logs"
API_PID_FILE="$PID_DIR/api.pid"
WEB_PID_FILE="$PID_DIR/web.pid"
LOG_FILE="$PID_DIR/service.log"

mkdir -p "$PID_DIR"

log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" >> "$LOG_FILE"; }

stop_services() {
    local stopped=0
    for pidfile in "$API_PID_FILE" "$WEB_PID_FILE"; do
        if [ -f "$pidfile" ]; then
            pid=$(cat "$pidfile")
            if kill -0 "$pid" 2>/dev/null; then
                kill "$pid" 2>/dev/null
                stopped=1
            fi
            rm -f "$pidfile"
        fi
    done
    # Also kill anything on the ports as a safety net
    { lsof -ti:8000 | xargs kill 2>/dev/null; } || true
    { lsof -ti:7860 | xargs kill 2>/dev/null; } || true
    [ "$stopped" -eq 1 ] && log "Services stopped." || true
}

start_services() {
    stop_services

    cd "$PROJECT_DIR"
    source .venv/bin/activate

    log "Starting FastAPI on port 8000..."
    uvicorn api.main:app --host 0.0.0.0 --port 8000 >> "$LOG_FILE" 2>&1 &
    echo $! > "$API_PID_FILE"

    log "Starting Next.js on port 7860..."
    cd web && npx next dev --port 7860 --hostname 0.0.0.0 >> "$LOG_FILE" 2>&1 &
    echo $! > "$WEB_PID_FILE"
    cd "$PROJECT_DIR"

    log "Services started (API PID=$(cat "$API_PID_FILE"), Web PID=$(cat "$WEB_PID_FILE"))."
}

status_services() {
    running=0
    for name_pid in "API:$API_PID_FILE" "Web:$WEB_PID_FILE"; do
        name="${name_pid%%:*}"
        pidfile="${name_pid#*:}"
        if [ -f "$pidfile" ] && kill -0 "$(cat "$pidfile")" 2>/dev/null; then
            echo "$name: running (PID $(cat "$pidfile"))"
            running=1
        else
            echo "$name: stopped"
        fi
    done
    return $((1 - running))
}

case "${1:-start}" in
    start)  start_services ;;
    stop)   stop_services ;;
    status) status_services ;;
    *)      echo "Usage: $0 {start|stop|status}" ;;
esac
