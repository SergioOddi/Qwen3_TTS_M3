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
