import time
from app.jobs import JobQueue


def _wait(q, jid, timeout=5):
    end = time.time() + timeout
    while time.time() < end:
        job = q.get(jid)
        if job["status"] in ("done", "error"):
            return job
        time.sleep(0.02)
    raise AssertionError("job non terminato")


def test_job_success_sets_result():
    q = JobQueue()
    jid = q.submit(lambda progress: "OUTPUT/x.wav")
    job = _wait(q, jid)
    assert job["status"] == "done"
    assert job["result"] == "OUTPUT/x.wav"


def test_job_error_captured():
    q = JobQueue()
    def boom(progress):
        raise RuntimeError("fallito")
    jid = q.submit(boom)
    job = _wait(q, jid)
    assert job["status"] == "error"
    assert "fallito" in job["error"]


def test_progress_updates():
    q = JobQueue()
    def work(progress):
        progress(0.5)
        return "ok"
    jid = q.submit(work)
    job = _wait(q, jid)
    assert job["progress"] == 1.0  # forzato a 1 al termine
