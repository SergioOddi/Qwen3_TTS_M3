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
