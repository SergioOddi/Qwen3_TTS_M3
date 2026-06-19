"""App desktop GASSMANN: finestra nativa (pywebview) + server FastAPI in background.

Avvio: python -m app.desktop  (oppure doppio-click su GASSMANN.command)
"""
import socket
import threading
import time
import urllib.request

import uvicorn
import webview

from app.main import create_app

HOST = "127.0.0.1"


def _free_port() -> int:
    # ponytail: chiede al SO una porta libera, niente gestione conflitti
    s = socket.socket()
    s.bind((HOST, 0))
    port = s.getsockname()[1]
    s.close()
    return port


def _wait_ready(url: str, timeout: float = 30.0) -> None:
    """Aspetta che il server risponda, evita finestra bianca."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            urllib.request.urlopen(url, timeout=1)
            return
        except Exception:
            time.sleep(0.2)
    raise RuntimeError(f"Server non pronto entro {timeout}s su {url}")


def main() -> None:
    port = _free_port()
    url = f"http://{HOST}:{port}"

    server = uvicorn.Server(uvicorn.Config(create_app(), host=HOST, port=port, log_level="warning"))
    threading.Thread(target=server.run, daemon=True).start()

    _wait_ready(url)
    webview.create_window("GASSMANN", url, width=1100, height=820)
    webview.start()  # blocca sul main thread (richiesto su macOS)


if __name__ == "__main__":
    main()
