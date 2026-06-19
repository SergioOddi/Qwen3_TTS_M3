"""Path centralizzati del progetto, risolti rispetto alla root del repo."""
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CONFIG_DIR = PROJECT_ROOT / "config"
OUTPUT_DIR = PROJECT_ROOT / "OUTPUT"
SAMPLES_DIR = PROJECT_ROOT / "VOICE_SAMPLES"

for _d in (OUTPUT_DIR, SAMPLES_DIR):
    _d.mkdir(parents=True, exist_ok=True)
