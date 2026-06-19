#!/usr/bin/env bash
# Doppio-click in Finder per avviare GASSMANN (si apre nel browser).
# Chiudi questa finestra di Terminale per fermare l'app.
cd "$(dirname "$0")"
source .venv/bin/activate
PORT="${PORT:-8000}"
# libera la porta da eventuali istanze rimaste appese
lsof -nP -tiTCP:"${PORT}" -sTCP:LISTEN 2>/dev/null | xargs kill -9 2>/dev/null || true
( sleep 3 && open "http://127.0.0.1:${PORT}" ) &
echo "GASSMANN avviato → http://127.0.0.1:${PORT}"
echo "(chiudi questa finestra per fermarlo)"
exec python -m uvicorn app.main:create_app --factory --host 127.0.0.1 --port "${PORT}"
