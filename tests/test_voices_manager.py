"""Check: export → rename → delete → import ricrea la voce (config + campione)."""
import json
import tempfile
from pathlib import Path

import numpy as np
import soundfile as sf

from app import config as appconfig
from app import voices


def test_manager_roundtrip():
    with tempfile.TemporaryDirectory() as d:
        root = Path(d)
        appconfig.PROJECT_ROOT = root
        appconfig.CONFIG_DIR = root / "config"
        appconfig.SAMPLES_DIR = root / "VOICE_SAMPLES"
        appconfig.CONFIG_DIR.mkdir()
        appconfig.SAMPLES_DIR.mkdir()

        # voce finta: config clone + campione 0.5s
        sf.write(appconfig.SAMPLES_DIR / "tizio.wav", np.ones(12000, "float32"), 24000)
        (appconfig.CONFIG_DIR / "tizio.json").write_text(json.dumps({
            "mode": "voice_clone", "language": "Italian", "voice_name": "tizio",
            "prompt_speech_path": "VOICE_SAMPLES/tizio.wav",
            "ref_text": "ciao sono tizio", "tags": ["docente"],
        }), encoding="utf-8")

        bundle = voices.export_voice("tizio")
        assert bundle["samples"], "export deve includere il campione audio"

        # edit + rename
        info = voices.update_voice("tizio", new_id="caio", tags=["narratore"])
        assert info["id"] == "caio"
        assert voices.get_voice("tizio") is None
        assert "narratore" in voices.get_voice_edit("caio")["tags"]

        # delete: rimuove solo il config
        voices.delete_voice("caio")
        assert voices.get_voice("caio") is None

        # import dal bundle → ricrea "tizio" con campione riscritto in VOICE_SAMPLES
        re_info = voices.import_voice(bundle)
        assert re_info["id"] == "tizio"
        assert re_info["type"] == "clone"
        cfg = voices.load_config("tizio")
        assert (appconfig.PROJECT_ROOT / cfg["prompt_speech_path"]).exists()

        # bundle non valido → errore chiaro
        try:
            voices.import_voice({"foo": "bar"})
            assert False, "atteso ValueError"
        except ValueError:
            pass


def test_delete_removes_orphan_keeps_shared():
    with tempfile.TemporaryDirectory() as d:
        root = Path(d)
        appconfig.PROJECT_ROOT = root
        appconfig.CONFIG_DIR = root / "config"
        appconfig.SAMPLES_DIR = root / "VOICE_SAMPLES"
        appconfig.CONFIG_DIR.mkdir()
        appconfig.SAMPLES_DIR.mkdir()

        def voice(name, sample):
            sf.write(appconfig.SAMPLES_DIR / sample, np.ones(2400, "float32"), 24000)
            (appconfig.CONFIG_DIR / f"{name}.json").write_text(json.dumps({
                "mode": "voice_clone", "prompt_speech_path": f"VOICE_SAMPLES/{sample}",
                "ref_text": "x",
            }), encoding="utf-8")

        # due voci che condividono lo stesso campione + una con campione proprio
        voice("capone", "capone.wav")
        voice("capone_docente", "capone.wav")  # stesso sample
        voice("solo", "solo.wav")

        voices.delete_voice("capone")
        assert (appconfig.SAMPLES_DIR / "capone.wav").exists(), \
            "sample condiviso con capone_docente NON va cancellato"

        voices.delete_voice("solo")
        assert not (appconfig.SAMPLES_DIR / "solo.wav").exists(), \
            "sample orfano va cancellato"


if __name__ == "__main__":
    test_manager_roundtrip()
    test_delete_removes_orphan_keeps_shared()
    print("ok")
