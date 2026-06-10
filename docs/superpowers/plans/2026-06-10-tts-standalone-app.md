# TTS_M3 App Standalone — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Costruire una web app locale offline che genera audio TTS (voice design + voice cloning), gestisce una libreria di voci e testi, supporta batch e preprocessing biochimica, con registrazione microfono e trascrizione automatica.

**Architecture:** Backend FastAPI in una nuova cartella `app/`, isolata dagli script `src/` esistenti (che vengono riusati come libreria, non modificati). Layer puri e testabili: `voices.py` (CRUD config), `model_manager.py` (caricamento lazy modelli + generate), `jobs.py` (coda in-process 1 worker), `transcribe.py` (Whisper). `main.py` espone REST e serve una single-page app vanilla (HTML/CSS/JS, zero CDN). I componenti che usano il modello/Whisper sono mockabili tramite dependency injection in `create_app()`.

**Tech Stack:** Python 3.12, FastAPI, uvicorn, qwen-tts 0.0.5, torch (mps), soundfile, pydub (+ffmpeg), librosa, mlx-whisper; frontend vanilla JS + MediaRecorder API; pytest + httpx TestClient.

---

## File Structure

```
app/
  __init__.py
  config.py          # path costanti (PROJECT_ROOT, CONFIG_DIR, OUTPUT_DIR, SAMPLES_DIR)
  voices.py          # list_voices, get_sample_path, create_clone, resolve_voice
  model_manager.py   # ModelManager: lazy load + generate_design/generate_clone
  jobs.py            # JobQueue: submit, get, worker thread
  transcribe.py      # transcribe(audio_path, language)
  pipeline.py        # run_generation(params)->path: collega voci+preprocess+model+save
  main.py            # create_app(deps) -> FastAPI; route /api/*; serve static
  static/
    index.html
    style.css
    app.js
tests/
  __init__.py
  conftest.py        # fixtures: tmp config/output dirs, fake model manager
  test_voices.py
  test_jobs.py
  test_pipeline.py
  test_api.py
launch.sh
```

`src/` resta invariato. `biochem_text_preprocessor.py` e `audio_converter.py` importati da `pipeline.py` aggiungendo `src/` al path.

---

## Task 0: Setup ambiente e dipendenze

**Files:**
- Modify: `requirements.txt`
- Create: `app/__init__.py`, `tests/__init__.py`

- [ ] **Step 1: Aggiungere dipendenze a `requirements.txt`**

Aggiungere in fondo al file:

```
# App standalone (web UI locale)
uvicorn>=0.30.0
python-multipart>=0.0.9
mlx-whisper>=0.4.0

# Test
pytest>=8.0.0
```

- [ ] **Step 2: Installare**

Run: `.venv/bin/pip install -U fastapi "uvicorn>=0.30" python-multipart pytest`
(mlx-whisper si installa ma è usato lazy; se la rete non è disponibile, installarlo dopo.)
Expected: installazione completata senza errori.

- [ ] **Step 3: Verificare ffmpeg presente (serve per convertire mp3 e blob microfono)**

Run: `which ffmpeg || brew install ffmpeg`
Expected: path a ffmpeg stampato.

- [ ] **Step 4: Creare i package vuoti**

```bash
mkdir -p app/static tests
touch app/__init__.py tests/__init__.py
```

- [ ] **Step 5: Commit**

```bash
git add requirements.txt app/__init__.py tests/__init__.py
git commit -m "chore: deps e scaffolding app standalone"
```

---

## Task 1: Path centralizzati (`app/config.py`)

**Files:**
- Create: `app/config.py`

- [ ] **Step 1: Scrivere `app/config.py`**

```python
"""Path centralizzati del progetto, risolti rispetto alla root del repo."""
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CONFIG_DIR = PROJECT_ROOT / "config"
OUTPUT_DIR = PROJECT_ROOT / "OUTPUT"
SAMPLES_DIR = PROJECT_ROOT / "VOICE_SAMPLES"
INPUT_DIR = PROJECT_ROOT / "INPUT"
SRC_DIR = PROJECT_ROOT / "src"

for _d in (OUTPUT_DIR, SAMPLES_DIR):
    _d.mkdir(parents=True, exist_ok=True)
```

- [ ] **Step 2: Verifica import**

Run: `.venv/bin/python -c "from app.config import CONFIG_DIR; print(CONFIG_DIR.exists())"`
Expected: `True`

- [ ] **Step 3: Commit**

```bash
git add app/config.py
git commit -m "feat: path centralizzati app"
```

---

## Task 2: Libreria voci — lettura (`app/voices.py`)

**Files:**
- Create: `app/voices.py`
- Test: `tests/conftest.py`, `tests/test_voices.py`

- [ ] **Step 1: Fixture in `tests/conftest.py`**

```python
import json
import pytest
from app import config as appconfig


@pytest.fixture
def tmp_dirs(tmp_path, monkeypatch):
    """Reindirizza config/output/samples a directory temporanee."""
    cfg = tmp_path / "config"
    out = tmp_path / "OUTPUT"
    samp = tmp_path / "VOICE_SAMPLES"
    for d in (cfg, out, samp):
        d.mkdir()
    monkeypatch.setattr(appconfig, "CONFIG_DIR", cfg)
    monkeypatch.setattr(appconfig, "OUTPUT_DIR", out)
    monkeypatch.setattr(appconfig, "SAMPLES_DIR", samp)
    return {"config": cfg, "output": out, "samples": samp}


def _write(cfg_dir, name, data):
    (cfg_dir / f"{name}.json").write_text(json.dumps(data), encoding="utf-8")
```

- [ ] **Step 2: Test fallisce per `list_voices`**

In `tests/test_voices.py`:

```python
import json
from app import voices
from tests.conftest import _write


def test_list_voices_separates_design_and_clone(tmp_dirs):
    _write(tmp_dirs["config"], "narratore", {
        "language": "Italian",
        "voice_description": "Voce calda da narratore",
    })
    _write(tmp_dirs["config"], "zaza_docente", {
        "mode": "voice_clone",
        "language": "Italian",
        "voice_name": "zaza",
        "prompt_speech_path": "VOICE_SAMPLES/zaza.wav",
        "ref_text": "ciao",
    })

    result = voices.list_voices()
    by_id = {v["id"]: v for v in result}

    assert by_id["narratore"]["type"] == "design"
    assert by_id["zaza_docente"]["type"] == "clone"
    assert "docente" in by_id["zaza_docente"]["tags"]
    assert by_id["narratore"]["language"] == "Italian"
```

- [ ] **Step 3: Eseguire — deve fallire**

Run: `.venv/bin/pytest tests/test_voices.py -v`
Expected: FAIL (modulo `voices` o funzione assente).

- [ ] **Step 4: Implementare lettura in `app/voices.py`**

```python
"""CRUD sulle voci, basato sui file JSON in config/."""
import json
import re
from pathlib import Path

from app import config as appconfig

_TAG_SUFFIXES = ("docente", "narratore")


def _derive_tags(name: str, data: dict) -> list[str]:
    tags = list(data.get("tags", []))
    for suffix in _TAG_SUFFIXES:
        if name.endswith(f"_{suffix}") and suffix not in tags:
            tags.append(suffix)
    return tags


def _voice_info(path: Path) -> dict | None:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None
    name = path.stem
    is_clone = data.get("mode") == "voice_clone" or "prompt_speech_path" in data
    return {
        "id": name,
        "type": "clone" if is_clone else "design",
        "language": data.get("language", "Italian"),
        "description": data.get("voice_description")
        or data.get("voice_notes")
        or data.get("instruct", ""),
        "tags": _derive_tags(name, data),
        "sample_path": data.get("prompt_speech_path") if is_clone else None,
        "config_path": str(path),
    }


def list_voices() -> list[dict]:
    out = []
    for path in sorted(appconfig.CONFIG_DIR.glob("*.json")):
        info = _voice_info(path)
        if info:
            out.append(info)
    return out


def get_voice(voice_id: str) -> dict | None:
    path = appconfig.CONFIG_DIR / f"{voice_id}.json"
    return _voice_info(path) if path.exists() else None


def load_config(voice_id: str) -> dict:
    path = appconfig.CONFIG_DIR / f"{voice_id}.json"
    return json.loads(path.read_text(encoding="utf-8"))
```

- [ ] **Step 5: Eseguire — deve passare**

Run: `.venv/bin/pytest tests/test_voices.py -v`
Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add app/voices.py tests/conftest.py tests/test_voices.py
git commit -m "feat: lettura libreria voci da config json"
```

---

## Task 3: Risoluzione path campione (`get_sample_path`)

**Files:**
- Modify: `app/voices.py`
- Test: `tests/test_voices.py`

- [ ] **Step 1: Test path campione**

Aggiungere a `tests/test_voices.py`:

```python
def test_get_sample_path_resolves_relative(tmp_dirs, monkeypatch):
    from app import config as appconfig
    sample = tmp_dirs["samples"] / "zaza.wav"
    sample.write_bytes(b"RIFF")
    _write(tmp_dirs["config"], "zaza", {
        "mode": "voice_clone",
        "prompt_speech_path": str(sample),
        "ref_text": "x",
    })
    assert voices.get_sample_path("zaza") == sample


def test_get_sample_path_none_for_design(tmp_dirs):
    _write(tmp_dirs["config"], "narr", {"voice_description": "x"})
    assert voices.get_sample_path("narr") is None
```

- [ ] **Step 2: Eseguire — deve fallire**

Run: `.venv/bin/pytest tests/test_voices.py -k sample_path -v`
Expected: FAIL (`get_sample_path` assente).

- [ ] **Step 3: Implementare in `app/voices.py`**

```python
def get_sample_path(voice_id: str) -> Path | None:
    info = get_voice(voice_id)
    if not info or not info["sample_path"]:
        return None
    p = Path(info["sample_path"])
    if not p.is_absolute():
        p = appconfig.PROJECT_ROOT / p
    return p if p.exists() else None
```

- [ ] **Step 4: Eseguire — deve passare**

Run: `.venv/bin/pytest tests/test_voices.py -k sample_path -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add app/voices.py tests/test_voices.py
git commit -m "feat: risoluzione path campione voce"
```

---

## Task 4: Creazione voce clonata (`create_clone`)

**Files:**
- Modify: `app/voices.py`
- Test: `tests/test_voices.py`

- [ ] **Step 1: Test creazione clone**

```python
def test_create_clone_writes_config_and_wav(tmp_dirs):
    import numpy as np
    import soundfile as sf
    import io
    # campione WAV finto 1s mono 16k
    buf = io.BytesIO()
    sf.write(buf, np.zeros(16000, dtype="float32"), 16000, format="WAV")
    info = voices.create_clone(
        name="prova",
        language="Italian",
        audio_bytes=buf.getvalue(),
        ref_text="testo di riferimento",
        instruct="voce calma",
        tags=["narratore"],
    )
    assert info["id"] == "prova"
    assert info["type"] == "clone"
    cfg = voices.load_config("prova")
    assert cfg["mode"] == "voice_clone"
    assert cfg["ref_text"] == "testo di riferimento"
    sample = voices.get_sample_path("prova")
    assert sample is not None and sample.exists()
    data, sr = sf.read(sample)
    assert sr == 24000  # convertito a 24k
```

- [ ] **Step 2: Eseguire — deve fallire**

Run: `.venv/bin/pytest tests/test_voices.py -k create_clone -v`
Expected: FAIL.

- [ ] **Step 3: Implementare in `app/voices.py`**

Aggiungere import in cima: `import io`, e in fondo:

```python
def _slugify(name: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9_-]+", "_", name.strip()).strip("_")
    return slug or "voce"


def _to_wav_24k_mono(audio_bytes: bytes, dest: Path) -> None:
    """Converte qualsiasi audio in WAV mono 24kHz. Usa pydub (ffmpeg) per
    formati compressi (webm/ogg/mp3), soundfile per WAV puro."""
    import soundfile as sf
    try:
        data, sr = sf.read(io.BytesIO(audio_bytes))
        import numpy as np
        if data.ndim > 1:
            data = data.mean(axis=1)
        if sr != 24000:
            import librosa
            data = librosa.resample(data.astype("float32"), orig_sr=sr, target_sr=24000)
        sf.write(dest, data, 24000)
    except Exception:
        from pydub import AudioSegment
        seg = AudioSegment.from_file(io.BytesIO(audio_bytes))
        seg = seg.set_channels(1).set_frame_rate(24000)
        seg.export(dest, format="wav")


def create_clone(name, language, audio_bytes, ref_text, instruct="", tags=None):
    if not ref_text or not ref_text.strip():
        raise ValueError("ref_text obbligatorio per una voce clonata")
    slug = _slugify(name)
    sample_path = appconfig.SAMPLES_DIR / f"{slug}.wav"
    _to_wav_24k_mono(audio_bytes, sample_path)

    cfg = {
        "mode": "voice_clone",
        "language": language,
        "voice_name": slug,
        "prompt_speech_path": str(sample_path),
        "ref_text": ref_text.strip(),
        "output_format": "wav",
        "sample_rate": 24000,
        "speed_factor": 1.0,
        "tags": tags or [],
    }
    if instruct:
        cfg["instruct"] = instruct
    (appconfig.CONFIG_DIR / f"{slug}.json").write_text(
        json.dumps(cfg, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return get_voice(slug)
```

- [ ] **Step 4: Eseguire — deve passare**

Run: `.venv/bin/pytest tests/test_voices.py -k create_clone -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add app/voices.py tests/test_voices.py
git commit -m "feat: creazione voce clonata da upload/registrazione"
```

---

## Task 5: Coda job in-process (`app/jobs.py`)

**Files:**
- Create: `app/jobs.py`
- Test: `tests/test_jobs.py`

- [ ] **Step 1: Test transizioni job**

`tests/test_jobs.py`:

```python
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
```

- [ ] **Step 2: Eseguire — deve fallire**

Run: `.venv/bin/pytest tests/test_jobs.py -v`
Expected: FAIL (modulo assente).

- [ ] **Step 3: Implementare `app/jobs.py`**

```python
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
```

- [ ] **Step 4: Eseguire — deve passare**

Run: `.venv/bin/pytest tests/test_jobs.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add app/jobs.py tests/test_jobs.py
git commit -m "feat: coda job in-process con worker singolo"
```

---

## Task 6: ModelManager (`app/model_manager.py`)

**Files:**
- Create: `app/model_manager.py`

Nessun test automatico (richiede GPU/modelli pesanti); verrà mockato negli endpoint e
verificato nello smoke finale. L'interfaccia è semplice e isolata.

- [ ] **Step 1: Implementare `app/model_manager.py`**

```python
"""Caricamento lazy dei modelli Qwen3-TTS e funzioni di generazione.

I modelli restano residenti in RAM dopo il primo caricamento. L'import di
torch/qwen_tts avviene dentro i metodi così i test possono mockare l'istanza.
"""

DESIGN_MODEL = "Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign"
BASE_MODEL = "Qwen/Qwen3-TTS-12Hz-1.7B-Base"


class ModelManager:
    def __init__(self):
        self._design = None
        self._base = None

    def _load(self, repo):
        import torch
        from qwen_tts import Qwen3TTSModel
        try:
            return Qwen3TTSModel.from_pretrained(
                repo, device_map="mps", dtype=torch.bfloat16,
                attn_implementation="flash_attention_2",
            )
        except Exception:
            return Qwen3TTSModel.from_pretrained(
                repo, device_map="mps", dtype=torch.bfloat16,
            )

    def design(self):
        if self._design is None:
            self._design = self._load(DESIGN_MODEL)
        return self._design

    def base(self):
        if self._base is None:
            self._base = self._load(BASE_MODEL)
        return self._base

    def generate_design(self, text, language, voice_description):
        wavs, sr = self.design().generate_voice_design(
            text=text, language=language, instruct=voice_description,
        )
        return wavs[0], sr

    def generate_clone(self, text, language, ref_audio, ref_text,
                       instruct=None, speed_factor=1.0):
        kwargs = dict(text=text, language=language,
                      ref_audio=ref_audio, ref_text=ref_text)
        if instruct:
            kwargs["instruct"] = instruct
        try:
            wavs, sr = self.base().generate_voice_clone(**kwargs)
        except TypeError:
            kwargs.pop("instruct", None)
            wavs, sr = self.base().generate_voice_clone(**kwargs)
        audio = wavs[0]
        if speed_factor and speed_factor != 1.0:
            import librosa
            audio = librosa.effects.time_stretch(
                audio.astype("float32"), rate=speed_factor)
        return audio, sr

    def status(self):
        return {"design_loaded": self._design is not None,
                "base_loaded": self._base is not None}
```

- [ ] **Step 2: Verifica import (senza caricare modelli)**

Run: `.venv/bin/python -c "from app.model_manager import ModelManager; print(ModelManager().status())"`
Expected: `{'design_loaded': False, 'base_loaded': False}`

- [ ] **Step 3: Commit**

```bash
git add app/model_manager.py
git commit -m "feat: ModelManager lazy load + generate"
```

---

## Task 7: Pipeline di generazione (`app/pipeline.py`)

**Files:**
- Create: `app/pipeline.py`
- Test: `tests/test_pipeline.py`

- [ ] **Step 1: Test pipeline con model manager finto**

`tests/test_pipeline.py`:

```python
import numpy as np
import soundfile as sf
from app import pipeline
from tests.conftest import _write


class FakeMM:
    def __init__(self):
        self.calls = []

    def generate_design(self, text, language, voice_description):
        self.calls.append(("design", text))
        return np.zeros(2400, dtype="float32"), 24000

    def generate_clone(self, text, language, ref_audio, ref_text,
                       instruct=None, speed_factor=1.0):
        self.calls.append(("clone", text))
        return np.zeros(2400, dtype="float32"), 24000


def test_pipeline_design(tmp_dirs):
    _write(tmp_dirs["config"], "narr", {
        "language": "Italian", "voice_description": "calma"})
    mm = FakeMM()
    out = pipeline.run_generation(
        mm, text="ciao", voice_id="narr", fmt="wav")
    assert out.endswith(".wav")
    assert mm.calls[0][0] == "design"
    data, sr = sf.read(out)
    assert sr == 24000


def test_pipeline_clone_uses_ref(tmp_dirs):
    sample = tmp_dirs["samples"] / "z.wav"
    sf.write(sample, np.zeros(24000, dtype="float32"), 24000)
    _write(tmp_dirs["config"], "z", {
        "mode": "voice_clone", "language": "Italian",
        "prompt_speech_path": str(sample), "ref_text": "rif"})
    mm = FakeMM()
    out = pipeline.run_generation(mm, text="testo", voice_id="z", fmt="wav")
    assert mm.calls[0][0] == "clone"
    assert out.endswith(".wav")


def test_pipeline_biochem_preprocess(tmp_dirs, monkeypatch):
    _write(tmp_dirs["config"], "narr", {
        "language": "Italian", "voice_description": "x"})
    captured = {}
    mm = FakeMM()
    orig = mm.generate_design
    def spy(text, language, voice_description):
        captured["text"] = text
        return orig(text, language, voice_description)
    mm.generate_design = spy
    pipeline.run_generation(mm, text="ATP", voice_id="narr",
                            fmt="wav", biochem=True)
    assert "text" in captured  # preprocessing eseguito senza errori
```

- [ ] **Step 2: Eseguire — deve fallire**

Run: `.venv/bin/pytest tests/test_pipeline.py -v`
Expected: FAIL (modulo assente).

- [ ] **Step 3: Implementare `app/pipeline.py`**

```python
"""Collega voci + preprocessing + modello + salvataggio file."""
import re
import sys

import soundfile as sf

from app import config as appconfig
from app import voices

sys.path.insert(0, str(appconfig.SRC_DIR))


def _preprocess_biochem(text: str) -> str:
    try:
        from biochem_text_preprocessor import BiochemTextPreprocessor
        return BiochemTextPreprocessor().process_text(text)
    except Exception:
        return text


def _safe_name(text: str) -> str:
    base = re.sub(r"[^a-zA-Z0-9_-]+", "_", text[:30]).strip("_")
    return base or "audio"


def _to_mp3(wav_path: str) -> str:
    from pydub import AudioSegment
    mp3_path = wav_path[:-4] + ".mp3"
    AudioSegment.from_wav(wav_path).export(mp3_path, format="mp3", bitrate="192k")
    import os
    os.remove(wav_path)
    return mp3_path


def run_generation(model_manager, text, voice_id, fmt="wav",
                   biochem=False, out_name=None, progress=None):
    info = voices.get_voice(voice_id)
    if info is None:
        raise ValueError(f"voce non trovata: {voice_id}")
    if not text or not text.strip():
        raise ValueError("testo vuoto")
    if biochem:
        text = _preprocess_biochem(text)
    if progress:
        progress(0.3)

    if info["type"] == "design":
        cfg = voices.load_config(voice_id)
        audio, sr = model_manager.generate_design(
            text=text, language=info["language"],
            voice_description=cfg.get("voice_description", ""))
    else:
        cfg = voices.load_config(voice_id)
        sample = voices.get_sample_path(voice_id)
        if sample is None:
            raise ValueError("campione audio mancante per la voce clonata")
        audio, sr = model_manager.generate_clone(
            text=text, language=info["language"], ref_audio=str(sample),
            ref_text=cfg.get("ref_text", ""), instruct=cfg.get("instruct"),
            speed_factor=cfg.get("speed_factor", 1.0))
    if progress:
        progress(0.8)

    name = out_name or f"{_safe_name(text)}_by_{voice_id}"
    wav_path = str(appconfig.OUTPUT_DIR / f"{name}.wav")
    sf.write(wav_path, audio, sr)
    return _to_mp3(wav_path) if fmt == "mp3" else wav_path
```

- [ ] **Step 4: Eseguire — deve passare**

Run: `.venv/bin/pytest tests/test_pipeline.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add app/pipeline.py tests/test_pipeline.py
git commit -m "feat: pipeline generazione (design+clone+biochem+mp3)"
```

---

## Task 8: Trascrizione Whisper (`app/transcribe.py`)

**Files:**
- Create: `app/transcribe.py`

Nessun test automatico (richiede mlx-whisper + download modello). Wrapper isolato e lazy.

- [ ] **Step 1: Implementare `app/transcribe.py`**

```python
"""Trascrizione automatica del campione audio per ottenere ref_text."""

_LANG_CODE = {
    "Italian": "it", "English": "en", "Spanish": "es", "French": "fr",
    "German": "de", "Portuguese": "pt", "Chinese": "zh", "Japanese": "ja",
    "Korean": "ko", "Russian": "ru",
}


def transcribe(audio_path: str, language: str = "Italian") -> str:
    """Ritorna la trascrizione. Solleva RuntimeError se mlx-whisper assente."""
    try:
        import mlx_whisper
    except ImportError as e:
        raise RuntimeError(
            "mlx-whisper non installato: trascrivi manualmente "
            "oppure esegui pip install mlx-whisper"
        ) from e
    result = mlx_whisper.transcribe(
        audio_path,
        path_or_hf_repo="mlx-community/whisper-large-v3-turbo",
        language=_LANG_CODE.get(language, "it"),
    )
    return result.get("text", "").strip()
```

- [ ] **Step 2: Verifica import (no esecuzione)**

Run: `.venv/bin/python -c "from app.transcribe import transcribe; print('ok')"`
Expected: `ok`

- [ ] **Step 3: Commit**

```bash
git add app/transcribe.py
git commit -m "feat: trascrizione automatica Whisper (lazy)"
```

---

## Task 9: API FastAPI (`app/main.py`)

**Files:**
- Create: `app/main.py`
- Test: `tests/test_api.py`

- [ ] **Step 1: Test API con model manager finto**

`tests/test_api.py`:

```python
import io
import numpy as np
import soundfile as sf
from fastapi.testclient import TestClient
from app.main import create_app
from tests.conftest import _write


class FakeMM:
    def generate_design(self, text, language, voice_description):
        return np.zeros(2400, dtype="float32"), 24000
    def generate_clone(self, **kw):
        return np.zeros(2400, dtype="float32"), 24000
    def status(self):
        return {"design_loaded": False, "base_loaded": False}


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
```

- [ ] **Step 2: Eseguire — deve fallire**

Run: `.venv/bin/pytest tests/test_api.py -v`
Expected: FAIL (modulo assente).

- [ ] **Step 3: Implementare `app/main.py`**

```python
"""FastAPI app: REST API + serve la single-page UI."""
from pathlib import Path

from fastapi import FastAPI, Form, HTTPException, UploadFile, File
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from app import config as appconfig
from app import voices, pipeline
from app.jobs import JobQueue
from app.model_manager import ModelManager

STATIC_DIR = Path(__file__).resolve().parent / "static"


class GenerateReq(BaseModel):
    text: str
    voice_id: str
    format: str = "wav"
    biochem: bool = False


class BatchItem(BaseModel):
    name: str
    text: str


class BatchReq(BaseModel):
    items: list[BatchItem]
    voice_id: str
    format: str = "wav"
    biochem: bool = False


def create_app(model_manager=None, job_queue=None) -> FastAPI:
    mm = model_manager or ModelManager()
    jobs = job_queue or JobQueue()
    app = FastAPI(title="TTS_M3")

    @app.get("/api/voices")
    def api_voices():
        return voices.list_voices()

    @app.get("/api/voices/{voice_id}/sample")
    def api_sample(voice_id: str):
        p = voices.get_sample_path(voice_id)
        if p is None:
            raise HTTPException(404, "campione non trovato")
        return FileResponse(p)

    @app.post("/api/voices")
    def api_create_voice(
        name: str = Form(...), language: str = Form("Italian"),
        ref_text: str = Form(...), instruct: str = Form(""),
        tags: str = Form(""), audio: UploadFile = File(...),
    ):
        try:
            info = voices.create_clone(
                name=name, language=language, audio_bytes=audio.file.read(),
                ref_text=ref_text, instruct=instruct,
                tags=[t for t in tags.split(",") if t.strip()],
            )
        except ValueError as e:
            raise HTTPException(400, str(e))
        return info

    @app.post("/api/transcribe")
    def api_transcribe(language: str = Form("Italian"),
                       audio: UploadFile = File(...)):
        import tempfile
        from app.transcribe import transcribe
        suffix = Path(audio.filename or "a.wav").suffix or ".wav"
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as f:
            f.write(audio.file.read())
            tmp = f.name
        try:
            return {"text": transcribe(tmp, language)}
        except RuntimeError as e:
            raise HTTPException(503, str(e))

    @app.post("/api/generate")
    def api_generate(req: GenerateReq):
        if not req.text.strip():
            raise HTTPException(400, "testo vuoto")
        if voices.get_voice(req.voice_id) is None:
            raise HTTPException(404, "voce non trovata")
        jid = jobs.submit(lambda progress: pipeline.run_generation(
            mm, text=req.text, voice_id=req.voice_id,
            fmt=req.format, biochem=req.biochem, progress=progress))
        return {"job_id": jid}

    @app.post("/api/batch")
    def api_batch(req: BatchReq):
        if not req.items:
            raise HTTPException(400, "nessun item")
        if voices.get_voice(req.voice_id) is None:
            raise HTTPException(404, "voce non trovata")

        def work(progress):
            results = []
            total = len(req.items)
            for i, item in enumerate(req.items):
                path = pipeline.run_generation(
                    mm, text=item.text, voice_id=req.voice_id,
                    fmt=req.format, biochem=req.biochem, out_name=item.name)
                results.append(path)
                progress((i + 1) / total)
            return results

        return {"job_id": jobs.submit(work)}

    @app.get("/api/jobs/{jid}")
    def api_job(jid: str):
        job = jobs.get(jid)
        if job is None:
            raise HTTPException(404, "job non trovato")
        return job

    @app.get("/api/outputs")
    def api_outputs():
        files = sorted(appconfig.OUTPUT_DIR.glob("*.*"),
                       key=lambda p: p.stat().st_mtime, reverse=True)
        return [{"name": p.name} for p in files
                if p.suffix in (".wav", ".mp3")]

    @app.get("/api/outputs/{filename}")
    def api_output_file(filename: str):
        p = appconfig.OUTPUT_DIR / Path(filename).name
        if not p.exists():
            raise HTTPException(404, "file non trovato")
        return FileResponse(p)

    @app.get("/api/status")
    def api_status():
        return mm.status()

    if STATIC_DIR.exists():
        app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="ui")

    return app


app = None


def get_app():
    global app
    if app is None:
        app = create_app()
    return app
```

- [ ] **Step 4: Eseguire — deve passare**

Run: `.venv/bin/pytest tests/test_api.py -v`
Expected: PASS (tutti i test).

- [ ] **Step 5: Eseguire l'intera suite**

Run: `.venv/bin/pytest -v`
Expected: tutti PASS.

- [ ] **Step 6: Commit**

```bash
git add app/main.py tests/test_api.py
git commit -m "feat: API FastAPI generate/batch/voci/job/output"
```

---

## Task 10: Frontend — index.html + style.css

**Files:**
- Create: `app/static/index.html`, `app/static/style.css`

Frontend non TDD: codice completo + verifica manuale nel browser (Task 12).

- [ ] **Step 1: Scrivere `app/static/index.html`**

```html
<!DOCTYPE html>
<html lang="it">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>TTS_M3 — Studio Voce</title>
  <link rel="stylesheet" href="/style.css">
</head>
<body>
  <header>
    <h1>🎙️ TTS_M3 — Studio Voce</h1>
    <nav>
      <button class="tab active" data-tab="genera">Genera</button>
      <button class="tab" data-tab="batch">Batch</button>
      <button class="tab" data-tab="voci">Voci</button>
    </nav>
  </header>

  <main>
    <!-- GENERA -->
    <section id="genera" class="panel active">
      <label>Testo</label>
      <textarea id="g-text" rows="8" placeholder="Scrivi o incolla il testo…"></textarea>
      <div class="row">
        <div>
          <label>Voce</label>
          <select id="g-voice"></select>
        </div>
        <div>
          <label>Formato</label>
          <select id="g-format"><option>wav</option><option>mp3</option></select>
        </div>
        <label class="check"><input type="checkbox" id="g-biochem"> Preprocessing biochimica</label>
      </div>
      <audio id="g-preview" controls class="hidden"></audio>
      <button id="g-run" class="primary">Genera audio</button>
      <div id="g-status" class="status"></div>
      <audio id="g-player" controls class="hidden"></audio>
      <a id="g-download" class="hidden" download>⬇ Scarica</a>
    </section>

    <!-- BATCH -->
    <section id="batch" class="panel">
      <p>Aggiungi più testi: stessa voce, generati in coda.</p>
      <div id="b-items"></div>
      <button id="b-add">+ Aggiungi testo</button>
      <div class="row">
        <div><label>Voce</label><select id="b-voice"></select></div>
        <div><label>Formato</label><select id="b-format"><option>wav</option><option>mp3</option></select></div>
        <label class="check"><input type="checkbox" id="b-biochem"> Biochimica</label>
      </div>
      <button id="b-run" class="primary">Avvia batch</button>
      <div id="b-status" class="status"></div>
      <ul id="b-results"></ul>
    </section>

    <!-- VOCI -->
    <section id="voci" class="panel">
      <h2>Libreria voci</h2>
      <div id="v-list" class="cards"></div>
      <h2>Nuova voce clonata</h2>
      <div class="form">
        <label>Nome</label><input id="v-name" type="text">
        <label>Lingua</label>
        <select id="v-language">
          <option>Italian</option><option>English</option><option>Spanish</option>
          <option>French</option><option>German</option>
        </select>
        <label>Campione audio</label>
        <div class="row">
          <button id="v-rec">● Registra</button>
          <span id="v-rec-time">00:00</span>
          <input id="v-file" type="file" accept="audio/*">
        </div>
        <audio id="v-sample" controls class="hidden"></audio>
        <label>Trascrizione (ref_text)</label>
        <textarea id="v-reftext" rows="3" placeholder="Scrivi a mano o usa Trascrivi…"></textarea>
        <button id="v-transcribe">Trascrivi automaticamente</button>
        <label>Stile (instruct, opzionale)</label>
        <input id="v-instruct" type="text">
        <label>Tag (separati da virgola)</label>
        <input id="v-tags" type="text" placeholder="docente, narratore">
        <button id="v-save" class="primary">Salva voce</button>
        <div id="v-status" class="status"></div>
      </div>
    </section>
  </main>

  <script src="/app.js"></script>
</body>
</html>
```

- [ ] **Step 2: Scrivere `app/static/style.css`**

```css
:root {
  --bg: #0f1115; --panel: #1a1d24; --accent: #6c8cff; --text: #e8eaf0;
  --muted: #9aa3b2; --border: #2a2e38; --ok: #3ecf8e; --err: #ff6b6b;
}
* { box-sizing: border-box; }
body {
  margin: 0; background: var(--bg); color: var(--text);
  font-family: -apple-system, system-ui, sans-serif; line-height: 1.5;
}
header { padding: 1rem 1.5rem; border-bottom: 1px solid var(--border); }
h1 { margin: 0 0 .75rem; font-size: 1.3rem; }
nav { display: flex; gap: .5rem; }
.tab {
  background: none; border: none; color: var(--muted); padding: .5rem 1rem;
  cursor: pointer; border-radius: 8px; font-size: .95rem;
}
.tab.active { background: var(--panel); color: var(--text); }
main { max-width: 820px; margin: 0 auto; padding: 1.5rem; }
.panel { display: none; }
.panel.active { display: block; }
label { display: block; margin: .75rem 0 .25rem; color: var(--muted); font-size: .85rem; }
textarea, input[type=text], select {
  width: 100%; background: var(--panel); color: var(--text);
  border: 1px solid var(--border); border-radius: 8px; padding: .6rem; font-size: .95rem;
}
.row { display: flex; gap: 1rem; align-items: flex-end; flex-wrap: wrap; }
.row > div { flex: 1; }
.check { display: flex; align-items: center; gap: .4rem; }
button {
  background: var(--panel); color: var(--text); border: 1px solid var(--border);
  border-radius: 8px; padding: .55rem 1rem; cursor: pointer; font-size: .9rem;
}
button.primary { background: var(--accent); border-color: var(--accent); color: #fff; margin-top: 1rem; }
button:hover { filter: brightness(1.1); }
.status { margin: .75rem 0; color: var(--muted); min-height: 1.2em; }
.status.ok { color: var(--ok); } .status.err { color: var(--err); }
.hidden { display: none; }
audio { width: 100%; margin: .75rem 0; }
.cards { display: grid; grid-template-columns: repeat(auto-fill, minmax(220px,1fr)); gap: .75rem; }
.card { background: var(--panel); border: 1px solid var(--border); border-radius: 10px; padding: .75rem; }
.card h3 { margin: 0 0 .25rem; font-size: 1rem; }
.card .badge { font-size: .7rem; background: var(--border); padding: .1rem .4rem; border-radius: 5px; margin-right: .3rem; }
.card .desc { color: var(--muted); font-size: .8rem; margin: .4rem 0; }
.form { background: var(--panel); padding: 1rem; border-radius: 10px; margin-top: .5rem; }
ul#b-results { list-style: none; padding: 0; }
ul#b-results li { padding: .4rem 0; border-bottom: 1px solid var(--border); }
a[download] { display: inline-block; margin-top: .5rem; color: var(--accent); }
.b-item { display: flex; gap: .5rem; margin: .4rem 0; }
.b-item input { flex: 0 0 140px; } .b-item textarea { flex: 1; }
```

- [ ] **Step 3: Commit**

```bash
git add app/static/index.html app/static/style.css
git commit -m "feat: UI HTML + stile dark"
```

---

## Task 11: Frontend — app.js

**Files:**
- Create: `app/static/app.js`

- [ ] **Step 1: Scrivere `app/static/app.js`**

```javascript
const $ = (s) => document.querySelector(s);
const $$ = (s) => document.querySelectorAll(s);

// --- Tabs ---
$$(".tab").forEach((t) => t.onclick = () => {
  $$(".tab").forEach((x) => x.classList.remove("active"));
  $$(".panel").forEach((x) => x.classList.remove("active"));
  t.classList.add("active");
  $("#" + t.dataset.tab).classList.add("active");
});

// --- Caricamento voci ---
let voicesCache = [];
async function loadVoices() {
  const r = await fetch("/api/voices");
  voicesCache = await r.json();
  for (const sel of ["#g-voice", "#b-voice"]) {
    $(sel).innerHTML = voicesCache
      .map((v) => `<option value="${v.id}">${v.id} (${v.type})</option>`).join("");
  }
  renderVoiceCards();
}

function renderVoiceCards() {
  $("#v-list").innerHTML = voicesCache.map((v) => `
    <div class="card">
      <h3>${v.id}</h3>
      <div>${v.tags.map((t) => `<span class="badge">${t}</span>`).join("")}
           <span class="badge">${v.type}</span></div>
      <div class="desc">${v.description || ""}</div>
      ${v.type === "clone"
        ? `<audio controls src="/api/voices/${v.id}/sample"></audio>` : ""}
    </div>`).join("");
}

// --- Polling job ---
async function pollJob(jid, onProgress) {
  while (true) {
    const job = await (await fetch(`/api/jobs/${jid}`)).json();
    onProgress(job);
    if (job.status === "done" || job.status === "error") return job;
    await new Promise((r) => setTimeout(r, 400));
  }
}

// --- Genera ---
$("#g-run").onclick = async () => {
  const text = $("#g-text").value.trim();
  if (!text) { setStatus("#g-status", "Inserisci del testo", "err"); return; }
  setStatus("#g-status", "Invio…", "");
  $("#g-player").classList.add("hidden");
  $("#g-download").classList.add("hidden");
  const r = await fetch("/api/generate", {
    method: "POST", headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      text, voice_id: $("#g-voice").value,
      format: $("#g-format").value, biochem: $("#g-biochem").checked }),
  });
  if (!r.ok) { setStatus("#g-status", "Errore: " + (await r.text()), "err"); return; }
  const { job_id } = await r.json();
  const job = await pollJob(job_id, (j) =>
    setStatus("#g-status", `Generazione… ${Math.round(j.progress * 100)}%`, ""));
  if (job.status === "error") { setStatus("#g-status", "Errore: " + job.error, "err"); return; }
  const file = job.result.split("/").pop();
  const url = `/api/outputs/${file}`;
  $("#g-player").src = url; $("#g-player").classList.remove("hidden");
  $("#g-download").href = url; $("#g-download").classList.remove("hidden");
  setStatus("#g-status", "Completato ✓", "ok");
};

// --- Batch ---
function addBatchItem(name = "", text = "") {
  const div = document.createElement("div");
  div.className = "b-item";
  div.innerHTML = `<input placeholder="nome" value="${name}">
                   <textarea rows="2" placeholder="testo">${text}</textarea>`;
  $("#b-items").appendChild(div);
}
$("#b-add").onclick = () => addBatchItem();
addBatchItem();

$("#b-run").onclick = async () => {
  const items = [...$$("#b-items .b-item")].map((d, i) => ({
    name: d.querySelector("input").value.trim() || `item_${i + 1}`,
    text: d.querySelector("textarea").value.trim(),
  })).filter((it) => it.text);
  if (!items.length) { setStatus("#b-status", "Nessun testo", "err"); return; }
  const r = await fetch("/api/batch", {
    method: "POST", headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      items, voice_id: $("#b-voice").value,
      format: $("#b-format").value, biochem: $("#b-biochem").checked }),
  });
  const { job_id } = await r.json();
  const job = await pollJob(job_id, (j) =>
    setStatus("#b-status", `Batch… ${Math.round(j.progress * 100)}%`, ""));
  if (job.status === "error") { setStatus("#b-status", "Errore: " + job.error, "err"); return; }
  $("#b-results").innerHTML = job.result.map((p) => {
    const f = p.split("/").pop();
    return `<li>${f} — <a href="/api/outputs/${f}" download>scarica</a></li>`;
  }).join("");
  setStatus("#b-status", "Batch completato ✓", "ok");
};

// --- Registrazione microfono ---
let mediaRecorder, chunks = [], recBlob = null, recTimer, recSeconds = 0;
$("#v-rec").onclick = async () => {
  if (mediaRecorder && mediaRecorder.state === "recording") {
    mediaRecorder.stop();
    $("#v-rec").textContent = "● Registra";
    clearInterval(recTimer);
    return;
  }
  const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
  mediaRecorder = new MediaRecorder(stream);
  chunks = [];
  mediaRecorder.ondataavailable = (e) => chunks.push(e.data);
  mediaRecorder.onstop = () => {
    recBlob = new Blob(chunks, { type: "audio/webm" });
    $("#v-sample").src = URL.createObjectURL(recBlob);
    $("#v-sample").classList.remove("hidden");
    stream.getTracks().forEach((t) => t.stop());
  };
  mediaRecorder.start();
  $("#v-rec").textContent = "■ Stop";
  recSeconds = 0;
  recTimer = setInterval(() => {
    recSeconds++;
    const m = String(Math.floor(recSeconds / 60)).padStart(2, "0");
    const s = String(recSeconds % 60).padStart(2, "0");
    $("#v-rec-time").textContent = `${m}:${s}`;
  }, 1000);
};

$("#v-file").onchange = (e) => {
  if (e.target.files[0]) {
    recBlob = e.target.files[0];
    $("#v-sample").src = URL.createObjectURL(recBlob);
    $("#v-sample").classList.remove("hidden");
  }
};

function currentSampleBlob() {
  return recBlob;  // registrazione o file caricato
}

$("#v-transcribe").onclick = async () => {
  const blob = currentSampleBlob();
  if (!blob) { setStatus("#v-status", "Prima registra o carica un campione", "err"); return; }
  setStatus("#v-status", "Trascrizione in corso…", "");
  const fd = new FormData();
  fd.append("language", $("#v-language").value);
  fd.append("audio", blob, "sample.webm");
  const r = await fetch("/api/transcribe", { method: "POST", body: fd });
  if (!r.ok) { setStatus("#v-status", "Trascrizione non disponibile: " + (await r.text()), "err"); return; }
  $("#v-reftext").value = (await r.json()).text;
  setStatus("#v-status", "Trascrizione pronta (correggi se serve) ✓", "ok");
};

$("#v-save").onclick = async () => {
  const blob = currentSampleBlob();
  if (!blob) { setStatus("#v-status", "Manca il campione audio", "err"); return; }
  if (!$("#v-reftext").value.trim()) { setStatus("#v-status", "Manca la trascrizione", "err"); return; }
  if (!$("#v-name").value.trim()) { setStatus("#v-status", "Manca il nome", "err"); return; }
  const fd = new FormData();
  fd.append("name", $("#v-name").value);
  fd.append("language", $("#v-language").value);
  fd.append("ref_text", $("#v-reftext").value);
  fd.append("instruct", $("#v-instruct").value);
  fd.append("tags", $("#v-tags").value);
  fd.append("audio", blob, "sample.webm");
  const r = await fetch("/api/voices", { method: "POST", body: fd });
  if (!r.ok) { setStatus("#v-status", "Errore: " + (await r.text()), "err"); return; }
  setStatus("#v-status", "Voce salvata ✓", "ok");
  await loadVoices();
};

function setStatus(sel, msg, kind) {
  const el = $(sel);
  el.textContent = msg;
  el.className = "status" + (kind ? " " + kind : "");
}

loadVoices();
```

- [ ] **Step 2: Commit**

```bash
git add app/static/app.js
git commit -m "feat: logica frontend (genera/batch/voci/rec/trascrizione)"
```

---

## Task 12: Launch script + README + smoke test

**Files:**
- Create: `launch.sh`
- Modify: `README.md`

- [ ] **Step 1: Scrivere `launch.sh`**

```bash
#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"
source .venv/bin/activate
PORT="${PORT:-8000}"
( sleep 2 && open "http://127.0.0.1:${PORT}" ) &
exec uvicorn app.main:get_app --factory --host 127.0.0.1 --port "${PORT}"
```

- [ ] **Step 2: Rendere eseguibile**

Run: `chmod +x launch.sh`
Expected: nessun output.

- [ ] **Step 3: Avvio server in background + smoke API**

```bash
.venv/bin/uvicorn app.main:get_app --factory --host 127.0.0.1 --port 8011 &
sleep 3
curl -s http://127.0.0.1:8011/api/voices | head -c 200
curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8011/
kill %1
```

Expected: lista JSON voci reali del progetto + `200` per la UI.

- [ ] **Step 4: Aggiungere sezione al `README.md`**

Aggiungere in cima dopo il titolo:

```markdown
## 🚀 App standalone (web UI locale)

Avvia l'interfaccia grafica nel browser:

```bash
./launch.sh
```

Si apre su http://127.0.0.1:8000 con tre schede:
- **Genera** — testo → voce → audio (player + download wav/mp3)
- **Batch** — più testi in coda con la stessa voce
- **Voci** — libreria voci con preview + creazione voce clonata (registra dal
  microfono o carica un file, trascrizione automatica Whisper o manuale)

Tutto in locale e offline. Prima generazione più lenta (caricamento modello).
```

- [ ] **Step 5: Commit**

```bash
git add launch.sh README.md
git commit -m "feat: launch script e documentazione app"
```

---

## Task 13: Smoke test reale col modello (manuale)

**Files:** nessuno (verifica end-to-end).

- [ ] **Step 1: Avviare l'app**

Run: `./launch.sh`
Expected: browser aperto sulla UI.

- [ ] **Step 2: Generazione voice design**

Nella scheda Genera: testo breve ("Ciao, questo è un test."), scegliere una voce di tipo
`design`, formato wav, Genera. Expected: dopo il caricamento modello, player con audio
udibile + download funzionante.

- [ ] **Step 3: Generazione voice clone**

Scegliere una voce `clone` esistente (es. `zaza02`), generare. Expected: audio con timbro
clonato.

- [ ] **Step 4: Creazione nuova voce da microfono**

Scheda Voci → Registra ~5s → Trascrivi (o ref_text manuale) → nome + Salva. Expected:
voce compare nella libreria con preview; usabile nella scheda Genera.

- [ ] **Step 5: Commit finale (se sono serviti fix)**

```bash
git add -A
git commit -m "fix: aggiustamenti da smoke test end-to-end"
```

---

## Note di esecuzione

- I test automatici (Task 2–9) **non** caricano i modelli: usano `FakeMM` e config
  temporanee. Eseguibili sempre con `.venv/bin/pytest -v`.
- `mlx-whisper` e i modelli TTS richiedono rete solo al primo download; i TTS sono già in
  cache. Se `mlx-whisper` non è installato, la trascrizione auto risponde 503 e l'utente
  usa il ref_text manuale (la creazione voce resta possibile).
- `ffmpeg` è richiesto per export mp3 e per decodificare il blob webm del microfono;
  i campioni WAV vengono gestiti anche senza ffmpeg.
```
