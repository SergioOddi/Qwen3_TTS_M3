"""FastAPI app: REST API + serve la single-page UI."""
from pathlib import Path
from typing import Literal

from fastapi import FastAPI, Form, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from app import config as appconfig
from app import voices, pipeline
from app.jobs import JobQueue
from app.model_manager import ModelManager

STATIC_DIR = Path(__file__).resolve().parent / "static"


def _warm(mm):
    try:
        mm.base()
    except Exception:  # noqa: BLE001 — warmup best-effort, non deve mai bloccare l'app
        pass


class GenerateReq(BaseModel):
    text: str
    voice_id: str
    format: Literal["wav", "mp3"] = "wav"
    biochem: bool = False
    speed: float = 1.0
    instruct: str | None = None
    emotion: str | None = None
    temperature: float | None = None
    pitch: float | None = None   # DSP: semitoni (+/-)
    gain: float | None = None    # DSP: dB (+/-)


class UpdateVoiceReq(BaseModel):
    new_id: str | None = None
    language: str | None = None
    tags: list[str] | None = None
    description: str | None = None
    ref_text: str | None = None
    instruct: str | None = None


class BatchItem(BaseModel):
    name: str
    text: str


class BatchReq(BaseModel):
    items: list[BatchItem]
    voice_id: str
    format: Literal["wav", "mp3"] = "wav"
    biochem: bool = False
    emotion: str | None = None


class TeatroBlock(BaseModel):
    character: str = ""
    voice_id: str
    text: str
    speed: float = 1.0
    emotion: str | None = None     # chiave emozione (es. "felice")
    instruct: str | None = None    # istruzione libera (solo voci design)
    temperature: float | None = None  # espressività (sampling)
    pause_after: float = 0.5
    clip: str | None = None        # filename clip già generato (riusa, non rigenera)


class TeatroReq(BaseModel):
    blocks: list[TeatroBlock]
    format: Literal["wav", "mp3"] = "wav"
    title: str = "scena"


def create_app(model_manager=None, job_queue=None) -> FastAPI:
    mm = model_manager or ModelManager()
    jobs = job_queue or JobQueue()
    app = FastAPI(title="GASSMANN")

    # Pre-warm del modello Base (voce-clone) in background: la 1ª generazione paga
    # il load lazy (~decine di s su MPS), così invece avviene allo startup.
    # Solo per il ModelManager reale → i test (FakeMM) non caricano nulla.
    if isinstance(mm, ModelManager):
        import threading
        threading.Thread(target=_warm, args=(mm,), daemon=True).start()

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
                tags=[t.strip() for t in tags.split(",") if t.strip()],
            )
        except ValueError as e:
            raise HTTPException(400, str(e))
        return info

    @app.get("/api/voices/{voice_id}/config")
    def api_voice_config(voice_id: str):
        data = voices.get_voice_edit(voice_id)
        if data is None:
            raise HTTPException(404, "voce non trovata")
        return data

    @app.patch("/api/voices/{voice_id}")
    def api_update_voice(voice_id: str, req: UpdateVoiceReq):
        try:
            return voices.update_voice(
                voice_id, new_id=req.new_id, language=req.language, tags=req.tags,
                description=req.description, ref_text=req.ref_text, instruct=req.instruct)
        except ValueError as e:
            raise HTTPException(400, str(e))

    @app.delete("/api/voices/{voice_id}")
    def api_delete_voice(voice_id: str):
        try:
            voices.delete_voice(voice_id)
        except ValueError as e:
            raise HTTPException(404, str(e))
        return {"ok": True}

    @app.get("/api/voices/{voice_id}/export")
    def api_export_voice(voice_id: str):
        try:
            return voices.export_voice(voice_id)
        except ValueError as e:
            raise HTTPException(404, str(e))

    @app.post("/api/voices/import")
    def api_import_voice(file: UploadFile = File(...)):
        import json as _json
        try:
            bundle = _json.loads(file.file.read())
        except _json.JSONDecodeError:
            raise HTTPException(400, "file JSON non valido")
        try:
            return voices.import_voice(bundle)
        except ValueError as e:
            raise HTTPException(400, str(e))

    @app.post("/api/voices/{voice_id}/emotion")
    def api_add_emotion(
        voice_id: str, emotion: str = Form(...),
        ref_text: str = Form(...), audio: UploadFile = File(...),
    ):
        try:
            return voices.add_emotion_sample(
                voice_id, emotion, audio.file.read(), ref_text)
        except ValueError as e:
            raise HTTPException(400, str(e))

    @app.post("/api/generate")
    def api_generate(req: GenerateReq):
        if not req.text.strip():
            raise HTTPException(400, "testo vuoto")
        if voices.get_voice(req.voice_id) is None:
            raise HTTPException(404, "voce non trovata")
        jid = jobs.submit(lambda progress: pipeline.run_generation(
            mm, text=req.text, voice_id=req.voice_id,
            fmt=req.format, biochem=req.biochem, speed=req.speed,
            instruct=req.instruct, emotion=req.emotion,
            temperature=req.temperature, pitch=req.pitch, gain=req.gain,
            progress=progress))
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
                    fmt=req.format, biochem=req.biochem, out_name=item.name,
                    emotion=req.emotion)
                results.append(path)
                progress((i + 1) / total)
            return results

        return {"job_id": jobs.submit(work)}

    @app.post("/api/teatro")
    def api_teatro(req: TeatroReq):
        blocks = [b for b in req.blocks if b.text.strip()]
        if not blocks:
            raise HTTPException(400, "nessuna battuta")
        # Stitch-puro: unisce SOLO i clip già generati (via "↻ Rigenera"). Niente
        # generazione TTS qui — la scena è un montaggio, non rifà le battute.
        clips = []
        for i, b in enumerate(blocks):
            if not b.clip:
                raise HTTPException(400, f"battuta {i+1} non ancora generata: usa ↻ Rigenera")
            clip = appconfig.OUTPUT_DIR / Path(b.clip).name
            if not clip.exists():
                raise HTTPException(400, f"clip mancante per battuta {i+1}: rigenerala")
            clips.append(str(clip))
        pauses = [b.pause_after for b in blocks]

        def work(progress):
            scene = pipeline.stitch_scene(clips, pauses, req.title, fmt=req.format)
            progress(1.0)
            return {"scene": scene,
                    "clips": [{"character": b.character, "path": c}
                              for b, c in zip(blocks, clips)]}

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

    if STATIC_DIR.exists():
        app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="ui")

    return app
