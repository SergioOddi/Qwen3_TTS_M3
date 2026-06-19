"""Check: apply_emotion_dsp altera l'audio e resta nei limiti [-1,1]."""
import numpy as np

from app.pipeline import apply_emotion_dsp, EMOTION_DSP


def test_dsp_changes_and_clips():
    sr = 24000
    t = np.linspace(0, 1, sr, dtype="float32")
    y = 0.9 * np.sin(2 * np.pi * 220 * t)  # tono 220Hz

    # neutro/assente: nessuna modifica
    assert apply_emotion_dsp(y, sr, "neutro") is y

    out = apply_emotion_dsp(y, sr, "felice")  # tempo 1.05 -> più corto
    assert len(out) != len(y)
    assert out.max() <= 1.0 and out.min() >= -1.0

    # gain alto (arrabbiato 1.15) non deve superare il clip
    ang = apply_emotion_dsp(y, sr, "arrabbiato")
    assert ang.max() <= 1.0 and ang.min() >= -1.0
    assert set(EMOTION_DSP) <= {"felice", "triste", "arrabbiato", "impaurito",
                                "sorpreso", "ironico", "calmo"}


if __name__ == "__main__":
    test_dsp_changes_and_clips()
    print("ok")
