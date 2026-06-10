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
