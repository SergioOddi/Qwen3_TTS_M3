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


if __name__ == "__main__":
    test_manager_roundtrip()
    print("ok")
