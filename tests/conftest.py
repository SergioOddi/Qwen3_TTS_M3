import json
import pytest
from app import config as appconfig


@pytest.fixture
def tmp_dirs(tmp_path, monkeypatch):
    """Reindirizza config/output/samples a directory temporanee."""
    cfg = tmp_path / "config"
    out = tmp_path / "OUTPUT"
    samp = tmp_path / "VOICE_SAMPLES"
    for d in (cfg, out, samp):
        d.mkdir()
    monkeypatch.setattr(appconfig, "CONFIG_DIR", cfg)
    monkeypatch.setattr(appconfig, "OUTPUT_DIR", out)
    monkeypatch.setattr(appconfig, "SAMPLES_DIR", samp)
    return {"config": cfg, "output": out, "samples": samp}


def _write(cfg_dir, name, data):
    (cfg_dir / f"{name}.json").write_text(json.dumps(data), encoding="utf-8")
