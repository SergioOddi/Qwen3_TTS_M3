#!/usr/bin/env bash
# Doppio-click in Finder per aprire GASSMANN come app desktop.
set -e
cd "$(dirname "$0")"
source .venv/bin/activate
exec python -m app.desktop
