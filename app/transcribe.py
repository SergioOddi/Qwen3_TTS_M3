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
