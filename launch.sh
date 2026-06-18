#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"
source .venv/bin/activate
PORT="${PORT:-8000}"
( sleep 2 && open "http://127.0.0.1:${PORT}" ) &
exec uvicorn app.main:create_app --factory --host 127.0.0.1 --port "${PORT}"
