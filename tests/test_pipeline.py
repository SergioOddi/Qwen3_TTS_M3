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
    # Forza il preprocessing a un valore noto e verifica che arrivi al modello
    monkeypatch.setattr(pipeline, "_preprocess_biochem", lambda t: "PREPROCESSATO")
    mm = FakeMM()
    pipeline.run_generation(mm, text="ATP", voice_id="narr",
                            fmt="wav", biochem=True)
    assert mm.calls[0] == ("design", "PREPROCESSATO")


def test_pipeline_no_biochem_passes_text_unchanged(tmp_dirs, monkeypatch):
    _write(tmp_dirs["config"], "narr", {
        "language": "Italian", "voice_description": "x"})
    monkeypatch.setattr(pipeline, "_preprocess_biochem", lambda t: "NON_DEVE_USARSI")
    mm = FakeMM()
    pipeline.run_generation(mm, text="ciao", voice_id="narr", fmt="wav", biochem=False)
    assert mm.calls[0] == ("design", "ciao")


def test_pipeline_out_name_sanitized(tmp_dirs):
    """out_name malevolo non deve scrivere fuori da OUTPUT/."""
    _write(tmp_dirs["config"], "narr", {
        "language": "Italian", "voice_description": "x"})
    mm = FakeMM()
    out = pipeline.run_generation(
        mm, text="ciao", voice_id="narr", fmt="wav",
        out_name="../../../etc/evil")
    from app import config as appconfig
    # il file finisce dentro OUTPUT_DIR, senza componenti di path
    assert str(appconfig.OUTPUT_DIR) in out
    assert "etc/evil" not in out
