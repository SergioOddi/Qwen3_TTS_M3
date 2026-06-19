"""CRUD sulle voci, basato sui file JSON in config/."""
import base64
import binascii
import io
import json
import re
from pathlib import Path

from app import config as appconfig

_TAG_SUFFIXES = ("docente", "narratore")

# Emozioni supportate (chiavi condivise con frontend e pipeline)
ALLOWED_EMOTIONS = (
    "neutro", "felice", "triste", "arrabbiato",
    "impaurito", "sorpreso", "ironico", "calmo",
)
# Emozioni selezionabili (escluso "neutro" = voce base senza istruzione).
# Le voci design le supportano tutte via instruct (EMOTION_PHRASES in pipeline);
# le clone solo se hanno il relativo emotion_sample.
SELECTABLE_EMOTIONS = [e for e in ALLOWED_EMOTIONS if e != "neutro"]


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
        "gender": data.get("gender"),  # "male" | "female" | None (cloni)
        "sample_path": data.get("prompt_speech_path") if is_clone else None,
        # clone: solo emozioni con campione; design: tutte (emozione nativa via instruct)
        "emotions": sorted(data.get("emotion_samples", {})) if is_clone
        else list(SELECTABLE_EMOTIONS),
    }


def list_voices() -> list[dict]:
    out = []
    for path in sorted(appconfig.CONFIG_DIR.glob("*.json")):
        info = _voice_info(path)
        if info:
            out.append(info)
    return out


def _safe_voice_id(voice_id: str) -> bool:
    """Accetta solo id senza separatori di path o '..' (no path traversal)."""
    return bool(voice_id) and Path(voice_id).name == voice_id and ".." not in voice_id


def get_voice(voice_id: str) -> dict | None:
    if not _safe_voice_id(voice_id):
        return None
    path = appconfig.CONFIG_DIR / f"{voice_id}.json"
    return _voice_info(path) if path.exists() else None


def load_config(voice_id: str) -> dict:
    if not _safe_voice_id(voice_id):
        raise ValueError(f"voice_id non valido: {voice_id}")
    path = appconfig.CONFIG_DIR / f"{voice_id}.json"
    return json.loads(path.read_text(encoding="utf-8"))


def get_sample_path(voice_id: str) -> Path | None:
    info = get_voice(voice_id)
    if not info or not info["sample_path"]:
        return None
    p = _resolve(info["sample_path"])
    return p if p.exists() else None


def _resolve(relpath: str) -> Path:
    p = Path(relpath)
    return p if p.is_absolute() else appconfig.PROJECT_ROOT / p


def get_emotion_sample(voice_id: str, emotion: str | None):
    """Ritorna (Path, ref_text) del campione emotivo se la voce ne ha uno per
    questa emozione, altrimenti (None, None) → la pipeline usa il campione base."""
    if not emotion or emotion == "neutro":
        return None, None
    try:
        cfg = load_config(voice_id)
    except (ValueError, OSError, json.JSONDecodeError):
        return None, None
    rel = (cfg.get("emotion_samples") or {}).get(emotion)
    if not rel:
        return None, None
    p = _resolve(rel)
    if not p.exists():
        return None, None
    ref = (cfg.get("emotion_ref_texts") or {}).get(emotion) or cfg.get("ref_text", "")
    return p, ref


def add_emotion_sample(voice_id, emotion, audio_bytes, ref_text):
    """Aggiunge/aggiorna un campione emotivo a una voce clonata esistente."""
    info = get_voice(voice_id)
    if info is None or info["type"] != "clone":
        raise ValueError("voce clonata non trovata")
    if emotion not in ALLOWED_EMOTIONS or emotion == "neutro":
        raise ValueError(f"emozione non valida: {emotion}")
    if not ref_text or not ref_text.strip():
        raise ValueError("ref_text obbligatorio")
    sample_path = appconfig.SAMPLES_DIR / f"{voice_id}_{emotion}.wav"
    _to_wav_24k_mono(audio_bytes, sample_path)
    try:
        stored = str(sample_path.relative_to(appconfig.PROJECT_ROOT))
    except ValueError:
        stored = str(sample_path)
    cfg = load_config(voice_id)
    cfg.setdefault("emotion_samples", {})[emotion] = stored
    cfg.setdefault("emotion_ref_texts", {})[emotion] = ref_text.strip()
    (appconfig.CONFIG_DIR / f"{voice_id}.json").write_text(
        json.dumps(cfg, ensure_ascii=False, indent=2), encoding="utf-8")
    return {"voice_id": voice_id, "emotion": emotion,
            "emotions": sorted(cfg["emotion_samples"])}


def slugify(name: str, maxlen: int | None = None, default: str = "voce") -> str:
    s = name.strip()[:maxlen] if maxlen else name.strip()
    return re.sub(r"[^a-zA-Z0-9_-]+", "_", s).strip("_") or default


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
    slug = slugify(name)
    sample_path = appconfig.SAMPLES_DIR / f"{slug}.wav"
    _to_wav_24k_mono(audio_bytes, sample_path)

    try:
        stored_path = str(sample_path.relative_to(appconfig.PROJECT_ROOT))
    except ValueError:
        stored_path = str(sample_path)  # fuori dal repo (es. test): path assoluto
    cfg = {
        "mode": "voice_clone",
        "language": language,
        "voice_name": slug,
        "prompt_speech_path": stored_path,
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


# --- Manager voci: edit / rename / delete / export / import ---

def get_voice_edit(voice_id: str) -> dict | None:
    """Campi editabili (per pre-popolare l'editor della UI)."""
    if not _safe_voice_id(voice_id):
        return None
    path = appconfig.CONFIG_DIR / f"{voice_id}.json"
    if not path.exists():
        return None
    cfg = json.loads(path.read_text(encoding="utf-8"))
    is_clone = cfg.get("mode") == "voice_clone" or "prompt_speech_path" in cfg
    return {
        "id": voice_id,
        "type": "clone" if is_clone else "design",
        "language": cfg.get("language", "Italian"),
        "tags": cfg.get("tags", []),
        "description": (cfg.get("voice_notes") if is_clone
                        else cfg.get("voice_description")) or "",
        "ref_text": cfg.get("ref_text", ""),
        "instruct": cfg.get("instruct", ""),
    }


def update_voice(voice_id, *, new_id=None, language=None, tags=None,
                 description=None, ref_text=None, instruct=None) -> dict:
    """Modifica i campi e/o rinomina (cambia il file JSON = l'id della voce)."""
    if not _safe_voice_id(voice_id):
        raise ValueError("voice_id non valido")
    path = appconfig.CONFIG_DIR / f"{voice_id}.json"
    if not path.exists():
        raise ValueError("voce non trovata")
    cfg = json.loads(path.read_text(encoding="utf-8"))
    is_clone = cfg.get("mode") == "voice_clone" or "prompt_speech_path" in cfg

    if language is not None:
        cfg["language"] = language
    if tags is not None:
        cfg["tags"] = tags
    if ref_text is not None and ref_text.strip():
        cfg["ref_text"] = ref_text.strip()
    if instruct is not None:
        if instruct:
            cfg["instruct"] = instruct
        else:
            cfg.pop("instruct", None)
    if description is not None:
        cfg["voice_notes" if is_clone else "voice_description"] = description

    if new_id and new_id != voice_id:
        slug = slugify(new_id)
        if not _safe_voice_id(slug):
            raise ValueError("nome non valido")
        dest = appconfig.CONFIG_DIR / f"{slug}.json"
        # samefile: rename solo-maiuscole su FS case-insensitive (macOS) NON è
        # collisione, è lo stesso file. path.rename gestisce il cambio di case.
        if dest.exists() and not path.samefile(dest):
            raise ValueError("esiste già una voce con questo nome")
        cfg["voice_name"] = slug
        path.rename(dest)
        dest.write_text(json.dumps(cfg, ensure_ascii=False, indent=2), encoding="utf-8")
        return get_voice(slug)

    path.write_text(json.dumps(cfg, ensure_ascii=False, indent=2), encoding="utf-8")
    return get_voice(voice_id)


def delete_voice(voice_id: str) -> None:
    """Elimina solo il config. I campioni audio NON si toccano: sono spesso
    condivisi tra più voci (es. capone/capone_docente) o esterni a VOICE_SAMPLES.
    ponytail: orfani innocui; cancellarli romperebbe le voci sorelle."""
    if not _safe_voice_id(voice_id):
        raise ValueError("voice_id non valido")
    path = appconfig.CONFIG_DIR / f"{voice_id}.json"
    if not path.exists():
        raise ValueError("voce non trovata")
    path.unlink()


def _sample_rels(cfg: dict) -> list[str]:
    rels = [cfg["prompt_speech_path"]] if cfg.get("prompt_speech_path") else []
    rels += list((cfg.get("emotion_samples") or {}).values())
    return rels


def export_voice(voice_id: str) -> dict:
    """Bundle JSON autocontenuto: config + campioni audio in base64 (portabile)."""
    if not _safe_voice_id(voice_id):
        raise ValueError("voice_id non valido")
    path = appconfig.CONFIG_DIR / f"{voice_id}.json"
    if not path.exists():
        raise ValueError("voce non trovata")
    cfg = json.loads(path.read_text(encoding="utf-8"))
    samples = {}
    for rel in _sample_rels(cfg):
        p = _resolve(rel)
        if p.exists():
            samples[rel] = base64.b64encode(p.read_bytes()).decode("ascii")
    return {"gassmann_voice": 1, "id": voice_id, "config": cfg, "samples": samples}


def import_voice(bundle: dict) -> dict:
    """Ricrea una voce da un bundle export. Riscrive i campioni in VOICE_SAMPLES
    con un nuovo slug univoco e aggiorna i path nel config."""
    if not isinstance(bundle, dict) or bundle.get("gassmann_voice") != 1:
        raise ValueError("file voce non valido")
    cfg = dict(bundle.get("config") or {})
    samples = bundle.get("samples") or {}
    base = slugify(str(bundle.get("id") or cfg.get("voice_name") or "voce"))
    slug, i = base, 1
    while (appconfig.CONFIG_DIR / f"{slug}.json").exists():
        i += 1
        slug = f"{base}_{i}"
    cfg["voice_name"] = slug

    def _write_sample(rel, name):
        b64 = samples.get(rel)
        if not b64:
            return None
        try:
            raw = base64.b64decode(b64)
        except (binascii.Error, ValueError):
            raise ValueError("campione audio non valido nel file")
        dest = appconfig.SAMPLES_DIR / name
        dest.write_bytes(raw)
        try:
            return str(dest.relative_to(appconfig.PROJECT_ROOT))
        except ValueError:
            return str(dest)

    if cfg.get("prompt_speech_path"):
        new = _write_sample(cfg["prompt_speech_path"], f"{slug}.wav")
        if new:
            cfg["prompt_speech_path"] = new
    em = cfg.get("emotion_samples") or {}
    for emo, rel in list(em.items()):
        new = _write_sample(rel, f"{slug}_{emo}.wav")
        if new:
            em[emo] = new
    if em:
        cfg["emotion_samples"] = em

    (appconfig.CONFIG_DIR / f"{slug}.json").write_text(
        json.dumps(cfg, ensure_ascii=False, indent=2), encoding="utf-8")
    return get_voice(slug)
