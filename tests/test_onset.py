"""Check: _trim_onset_blip toglie il blip iniziale ma lascia intatto audio pulito."""
import numpy as np

from app.pipeline import _trim_onset_blip


def _tone(sr, ms, f=220, a=0.3):
    t = np.linspace(0, ms / 1000, int(sr * ms / 1000), dtype="float32")
    return (a * np.sin(2 * np.pi * f * t)).astype("float32")


def _sil(sr, ms):
    return np.zeros(int(sr * ms / 1000), dtype="float32")


def test_trim_blip_and_keep_clean():
    sr = 24000
    # blip 40ms + gap 80ms + voce 500ms → deve tagliare ~il blip
    clip = np.concatenate([_tone(sr, 40, f=400, a=0.2), _sil(sr, 80), _tone(sr, 500)])
    out = _trim_onset_blip(clip, sr)
    assert len(out) < len(clip), "deve tagliare il blip iniziale"
    assert len(clip) - len(out) <= int(sr * 0.09), "taglio <= ~90ms"

    # parte subito a parlare e non si ferma: intatto
    speech = _tone(sr, 800)
    assert _trim_onset_blip(speech, sr) is speech

    # parte in silenzio (nessun blip): intatto
    s = np.concatenate([_sil(sr, 50), _tone(sr, 500)])
    assert _trim_onset_blip(s, sr) is s


if __name__ == "__main__":
    test_trim_blip_and_keep_clean()
    print("ok")
