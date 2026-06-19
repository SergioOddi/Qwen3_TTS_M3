"""Collega voci + preprocessing + modello + salvataggio file."""
import soundfile as sf

from app import config as appconfig
from app import voices


# Frasi instruct per il modello VoiceDesign (le voci clone le ignorano)
EMOTION_PHRASES = {
    "neutro": "", "felice": "tono felice e gioioso",
    "triste": "tono triste e malinconico",
    "arrabbiato": "tono arrabbiato, voce tesa e concitata",
    "impaurito": "tono impaurito e tremante",
    "sorpreso": "tono sorpreso e incredulo",
    "ironico": "tono ironico e sarcastico",
    "calmo": "tono calmo e rilassato",
}

# Preset DSP (pitch in semitoni, tempo, gain) — fallback per voci clone senza
# campione emotivo. Euristici: tarare ascoltando l'output.
EMOTION_DSP = {
    "felice": (1.5, 1.05, 1.05), "triste": (-1.5, 0.95, 0.95),
    "arrabbiato": (0.5, 1.08, 1.15), "impaurito": (2.0, 1.10, 0.95),
    "sorpreso": (2.5, 1.05, 1.10), "ironico": (0.5, 0.98, 1.0),
    "calmo": (-0.5, 0.95, 0.98),
}


def apply_emotion_dsp(audio, sr, emotion):
    """Approssima l'emozione con pitch/tempo/gain. Crudo ma controllabile."""
    preset = EMOTION_DSP.get(emotion)
    if not preset:
        return audio
    import numpy as np
    import librosa
    n_steps, tempo, gain = preset
    y = audio.astype("float32")
    if n_steps:
        y = librosa.effects.pitch_shift(y, sr=sr, n_steps=n_steps)
    if tempo and tempo != 1.0:
        y = librosa.effects.time_stretch(y, rate=tempo)
    y = y * gain
    return np.clip(y, -1.0, 1.0)


def _preprocess_biochem(text: str) -> str:
    try:
        from app.biochem_text_preprocessor import BiochemTextPreprocessor
        return BiochemTextPreprocessor().process_text(text)
    except Exception:
        return text


def _safe_name(text: str) -> str:
    return voices.slugify(text, maxlen=30, default="audio")


def _to_mp3(wav_path: str) -> str:
    from pydub import AudioSegment
    mp3_path = wav_path[:-4] + ".mp3"
    AudioSegment.from_wav(wav_path).export(mp3_path, format="mp3", bitrate="192k")
    import os
    os.remove(wav_path)
    return mp3_path


def run_generation(model_manager, text, voice_id, fmt="wav",
                   biochem=False, out_name=None, progress=None, speed=None,
                   instruct=None, emotion=None, temperature=None):
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
        # design: l'emozione passa per instruct (frase + istruzione libera)
        instruct_final = ", ".join(x for x in [
            cfg.get("voice_description", ""), EMOTION_PHRASES.get(emotion, ""), instruct
        ] if x)
        audio, sr = model_manager.generate_design(
            text=text, language=info["language"],
            voice_description=instruct_final, temperature=temperature)
    else:
        cfg = voices.load_config(voice_id)
        # cascata emozione: campione emotivo (qualità reale) → altrimenti DSP fallback
        emo_sample, emo_ref = voices.get_emotion_sample(voice_id, emotion)
        if emo_sample is not None:
            ref_audio, ref_text, dsp_emotion = str(emo_sample), emo_ref, None
        else:
            base = voices.get_sample_path(voice_id)
            if base is None:
                raise ValueError("campione audio mancante per la voce clonata")
            ref_audio, ref_text, dsp_emotion = str(base), cfg.get("ref_text", ""), emotion
        speed_factor = speed if speed is not None else cfg.get("speed_factor", 1.0)
        audio, sr = model_manager.generate_clone(
            text=text, language=info["language"], ref_audio=ref_audio,
            ref_text=ref_text, speed_factor=speed_factor, temperature=temperature)
        if dsp_emotion:
            audio = apply_emotion_dsp(audio, sr, dsp_emotion)
    if progress:
        progress(0.8)

    name = _safe_name(out_name) if out_name else f"{_safe_name(text)}_by_{voice_id}"
    wav_path = str(appconfig.OUTPUT_DIR / f"{name}.wav")
    sf.write(wav_path, audio, sr)
    return _to_mp3(wav_path) if fmt == "mp3" else wav_path


def stitch_scene(clip_wavs, pauses, out_name, fmt="wav"):
    """Concatena i clip wav in una traccia unica, con silenzio (pauses[i] sec)
    dopo ogni clip. Ritorna il path della scena (wav o mp3)."""
    import numpy as np
    parts, sr = [], None
    for i, p in enumerate(clip_wavs):
        audio, sr = sf.read(p)
        parts.append(audio)
        pause = pauses[i] if i < len(pauses) else 0.0
        if pause > 0:
            silence_shape = (int(pause * sr),) + audio.shape[1:]
            parts.append(np.zeros(silence_shape, dtype=audio.dtype))
    scene = np.concatenate(parts) if parts else np.zeros(0)
    wav_path = str(appconfig.OUTPUT_DIR / f"{_safe_name(out_name)}.wav")
    sf.write(wav_path, scene, sr or 24000)
    return _to_mp3(wav_path) if fmt == "mp3" else wav_path
# ponytail: assume sr uniforme (24kHz dal modello) e lettura clip da disco;
# passare a stitch in-memory solo se i tempi lo richiedono (TTS domina comunque).
