#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
BACKEND_DIR="$ROOT_DIR/taskflow"
FRONTEND_DIR="$ROOT_DIR/taskflow-frontend"

BACKEND_HOST="127.0.0.1"
BACKEND_PORT="8000"
FRONTEND_PORT="3000"

log() {
  printf "[%s] %s\n" "$(date '+%Y-%m-%d %H:%M:%S')" "$1"
}

die() {
  log "ERROR: $1"
  exit 1
}

kill_port() {
  local port=$1
  local pids

  pids=$(lsof -t -i:"$port" || true)

  if [[ -n "$pids" ]]; then
    for pid in $pids; do
      log "Stopping process on port $port (PID $pid)"
      kill -9 "$pid"
    done
  fi
}

cleanup() {
  log "Shutting down services"
  [[ -n "${BACKEND_PID:-}" ]] && kill "$BACKEND_PID" 2>/dev/null || true
  [[ -n "${FRONTEND_PID:-}" ]] && kill "$FRONTEND_PID" 2>/dev/null || true
}

trap cleanup INT TERM

log "Preparing environment"

kill_port "$BACKEND_PORT"
kill_port "$FRONTEND_PORT"

# ---------------- Backend ----------------

log "Starting backend"
cd "$BACKEND_DIR" || die "Backend directory not found"

if [[ ! -d "venv" ]]; then
  log "Creating virtual environment"
  python3 -m venv venv || die "Failed to create virtualenv"
fi

source venv/bin/activate

pip install -r requirements.txt >/dev/null
python manage.py migrate >/dev/null

python manage.py runserver "$BACKEND_HOST:$BACKEND_PORT" \
  > "$ROOT_DIR/backend.log" 2>&1 &

BACKEND_PID=$!
deactivate

# ---------------- Frontend ----------------

log "Starting frontend"
cd "$FRONTEND_DIR" || die "Frontend directory not found"

npm install >/dev/null

npm run dev \
  > "$ROOT_DIR/frontend.log" 2>&1 &

FRONTEND_PID=$!

# ---------------- Status ----------------

log "System ready"
log "Backend   http://$BACKEND_HOST:$BACKEND_PORT"
log "Frontend  http://127.0.0.1:$FRONTEND_PORT"
log "Logs      backend.log | frontend.log"

wait

