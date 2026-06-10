"""Coda job in-process con un singolo worker (il modello non è concorrente)."""
import queue
import threading
import uuid


class JobQueue:
    def __init__(self):
        self._jobs: dict[str, dict] = {}
        self._q: queue.Queue = queue.Queue()
        self._lock = threading.Lock()
        self._worker = threading.Thread(target=self._run, daemon=True)
        self._worker.start()

    def submit(self, fn) -> str:
        """fn riceve un callback progress(float) e ritorna il path risultato."""
        jid = uuid.uuid4().hex[:12]
        with self._lock:
            self._jobs[jid] = {
                "id": jid, "status": "queued", "progress": 0.0,
                "result": None, "error": None,
            }
        self._q.put((jid, fn))
        return jid

    def get(self, jid: str) -> dict | None:
        with self._lock:
            job = self._jobs.get(jid)
            return dict(job) if job else None

    def _set(self, jid, **kw):
        with self._lock:
            self._jobs[jid].update(kw)

    def _run(self):
        while True:
            jid, fn = self._q.get()
            self._set(jid, status="running")
            try:
                result = fn(lambda p: self._set(jid, progress=float(p)))
                self._set(jid, status="done", progress=1.0, result=result)
            except Exception as e:  # noqa: BLE001
                self._set(jid, status="error", progress=1.0, error=str(e))
