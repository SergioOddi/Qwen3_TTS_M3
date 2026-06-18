"""Regression: generate_clone NON deve riusare un prompt cachato tra battute.
Il prompt item riusato si corrompe dopo la prima generate (la voce cambia tra
un rigenera e l'altro). Ogni generate deve ricevere ref_audio/ref_text freschi.
Run: python -m app.tests.test_clone_cache"""
import os
import tempfile

import numpy as np

from app.model_manager import ModelManager


class _FakeBase:
    def __init__(self):
        self.ref_audios = []

    def generate_voice_clone(self, text, language, ref_audio, ref_text, **kw):
        # nessun voice_clone_prompt: ref passato diretto, ri-encoding ogni volta
        assert "voice_clone_prompt" not in kw, "prompt cachato re-introdotto"
        self.ref_audios.append(ref_audio)
        return [np.zeros(2400, dtype="float32")], 24000


def _gen(mm, path):
    mm.generate_clone(text="ciao", language="Italian", ref_audio=path, ref_text="rif")


def main():
    fd, path = tempfile.mkstemp(suffix=".wav")
    os.close(fd)
    try:
        mm = ModelManager()
        fake = _FakeBase()
        mm._base = fake  # evita di caricare il modello reale
        _gen(mm, path); _gen(mm, path); _gen(mm, path)
        assert fake.ref_audios == [path, path, path], fake.ref_audios
    finally:
        os.unlink(path)
    print("ok")


if __name__ == "__main__":
    main()
