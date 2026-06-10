"""CRUD sulle voci, basato sui file JSON in config/."""
import io
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


def get_sample_path(voice_id: str) -> Path | None:
    info = get_voice(voice_id)
    if not info or not info["sample_path"]:
        return None
    p = Path(info["sample_path"])
    if not p.is_absolute():
        p = appconfig.PROJECT_ROOT / p
    return p if p.exists() else None


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
