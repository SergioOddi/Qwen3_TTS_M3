import io
import numpy as np
import soundfile as sf
from fastapi.testclient import TestClient
from app.main import create_app
from tests.conftest import _write


class FakeMM:
    def generate_design(self, text, language, voice_description, temperature=None):
        return np.zeros(2400, dtype="float32"), 24000
    def generate_clone(self, **kw):
        return np.zeros(2400, dtype="float32"), 24000


def _client(tmp_dirs):
    return TestClient(create_app(model_manager=FakeMM()))


def test_list_voices_endpoint(tmp_dirs):
    _write(tmp_dirs["config"], "narr", {"voice_description": "x"})
    r = _client(tmp_dirs).get("/api/voices")
    assert r.status_code == 200
    assert any(v["id"] == "narr" for v in r.json())


def test_generate_and_poll(tmp_dirs):
    _write(tmp_dirs["config"], "narr", {
        "language": "Italian", "voice_description": "x"})
    client = _client(tmp_dirs)
    r = client.post("/api/generate",
                    json={"text": "ciao", "voice_id": "narr", "format": "wav"})
    assert r.status_code == 200
    jid = r.json()["job_id"]
    # polling
    import time
    for _ in range(100):
        job = client.get(f"/api/jobs/{jid}").json()
        if job["status"] in ("done", "error"):
            break
        time.sleep(0.02)
    assert job["status"] == "done"


def test_generate_empty_text_400(tmp_dirs):
    _write(tmp_dirs["config"], "narr", {"voice_description": "x"})
    r = _client(tmp_dirs).post("/api/generate",
                               json={"text": "", "voice_id": "narr"})
    assert r.status_code == 400


def _poll(client, jid):
    import time
    for _ in range(100):
        job = client.get(f"/api/jobs/{jid}").json()
        if job["status"] in ("done", "error"):
            return job
        time.sleep(0.02)
    return job


def test_teatro_reuses_clip_no_regen(tmp_dirs, monkeypatch):
    """Se il blocco ha un clip già generato, /api/teatro lo riusa: nessuna
    nuova generazione TTS (altrimenti aggiunge casualità non controllabile)."""
    _write(tmp_dirs["config"], "narr", {"language": "Italian", "voice_description": "x"})
    sf.write(tmp_dirs["output"] / "battuta0.wav", np.zeros(2400, dtype="float32"), 24000)

    from app import pipeline
    def boom(*a, **k):
        raise AssertionError("run_generation non deve essere chiamato sul clip riusato")
    monkeypatch.setattr(pipeline, "run_generation", boom)

    client = _client(tmp_dirs)
    r = client.post("/api/teatro", json={"title": "scena", "format": "wav",
        "blocks": [{"voice_id": "narr", "text": "ciao", "clip": "battuta0.wav"}]})
    assert r.status_code == 200
    job = _poll(client, r.json()["job_id"])
    assert job["status"] == "done", job


def test_create_clone_endpoint(tmp_dirs):
    buf = io.BytesIO()
    sf.write(buf, np.zeros(16000, dtype="float32"), 16000, format="WAV")
    client = _client(tmp_dirs)
    r = client.post(
        "/api/voices",
        data={"name": "nuova", "language": "Italian",
              "ref_text": "testo rif", "tags": "narratore"},
        files={"audio": ("s.wav", buf.getvalue(), "audio/wav")},
    )
    assert r.status_code == 200
    assert r.json()["id"] == "nuova"
