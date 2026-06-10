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
                   biochem=False, out_name=None, progress=None, speed=None):
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
        speed_factor = speed if speed is not None else cfg.get("speed_factor", 1.0)
        audio, sr = model_manager.generate_clone(
            text=text, language=info["language"], ref_audio=str(sample),
            ref_text=cfg.get("ref_text", ""), instruct=cfg.get("instruct"),
            speed_factor=speed_factor)
    if progress:
        progress(0.8)

    name = _safe_name(out_name) if out_name else f"{_safe_name(text)}_by_{voice_id}"
    wav_path = str(appconfig.OUTPUT_DIR / f"{name}.wav")
    sf.write(wav_path, audio, sr)
    return _to_mp3(wav_path) if fmt == "mp3" else wav_path
