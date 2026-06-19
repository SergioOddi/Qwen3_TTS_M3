"""Check: stitch_scene concatena i clip con il silenzio giusto tra uno e l'altro."""
import os
import tempfile

import numpy as np
import soundfile as sf

from app.pipeline import stitch_scene


def test_stitch_lengths():
    sr = 24000
    a = np.ones(sr, dtype="float32")          # 1s
    b = np.ones(sr // 2, dtype="float32")     # 0.5s
    with tempfile.TemporaryDirectory() as d:
        pa, pb = os.path.join(d, "a.wav"), os.path.join(d, "b.wav")
        sf.write(pa, a, sr)
        sf.write(pb, b, sr)
        out = stitch_scene([pa, pb], [0.5, 0.0], "test_stitch_tmp", fmt="wav")
        try:
            scene, ssr = sf.read(out)
            assert ssr == sr
            # a + silenzio(0.5s) + b ; pausa dopo l'ultimo clip = 0
            assert len(scene) == len(a) + int(0.5 * sr) + len(b)
        finally:
            os.remove(out)


if __name__ == "__main__":
    test_stitch_lengths()
    print("ok")
