# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Stile di Comunicazione

**IMPORTANTE**:
- Risposte dirette e concise
- NON eseguire comandi automaticamente - aspettare richiesta esplicita dell'utente
- Limitarsi a dare informazioni essenziali, non spiegazioni lunghe

## Progetto Overview

Sistema TTS (Text-to-Speech) locale basato su Qwen3-TTS per generare voci in italiano e inglese su MacBook Pro M3 Max (36GB RAM unificata).

**Obiettivo**: Creare un'architettura user-friendly per la generazione vocale da file di testo con il modello Qwen3-TTS-12Hz-1.7B-VoiceDesign.

## Architettura del Progetto

```
TTS_M3/
├── INPUT/           # File .txt da convertire in audio
├── OUTPUT/          # File audio generati (.wav/.mp3)
├── config/          # File di configurazione per voci e parametri
├── src/             # Codice sorgente principale
└── models/          # Cache modelli scaricati (opzionale)
```

## Setup Ambiente

### Installazione Dipendenze
```bash
# Creare ambiente virtuale Python 3.12
conda create -n qwen3-tts python=3.12 -y
conda activate qwen3-tts

# Installare qwen-tts package
pip install -U qwen-tts

# Installare soundfile per salvare audio
pip install soundfile

# Per convertire .wav in .mp3 (opzionale)
pip install pydub
# Richiede anche ffmpeg: brew install ffmpeg
```

### Flash Attention 2 (Opzionale ma raccomandato)
```bash
# Su M3 Max con molta RAM, limitare jobs per evitare problemi
MAX_JOBS=4 pip install -U flash-attn --no-build-isolation
```

## Modelli Utilizzati

### Modello Principale: Qwen3-TTS-12Hz-1.7B-VoiceDesign
- **Capacità**: Voice design basato su descrizioni testuali
- **Lingue supportate**: Italiano, Inglese, e altre 8 lingue
- **Streaming**: Sì
- **Controllo tramite istruzioni**: Sì

### Download Modelli (opzionale - auto-download al primo uso)
```bash
# Download manuale se necessario
pip install -U modelscope
modelscope download --model Qwen/Qwen3-TTS-Tokenizer-12Hz --local_dir ./models/Qwen3-TTS-Tokenizer-12Hz
modelscope download --model Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign --local_dir ./models/Qwen3-TTS-12Hz-1.7B-VoiceDesign
```

## Utilizzo del Modello

### Voice Design - Esempio Base
```python
import torch
import soundfile as sf
from qwen_tts import Qwen3TTSModel

model = Qwen3TTSModel.from_pretrained(
    "Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign",
    device_map="mps",  # Usa Metal Performance Shaders su M3 Max
    dtype=torch.bfloat16,
    attn_implementation="flash_attention_2",  # se installato
)

# Generazione singola
wavs, sr = model.generate_voice_design(
    text="Testo da convertire in audio",
    language="Italian",  # o "English", "Chinese", etc.
    instruct="Descrizione della voce desiderata: voce maschile matura, tono caldo e professionale",
)
sf.write("output.wav", wavs[0], sr)
```

### Parametri di Configurazione Vocale

**Formato file di configurazione** (JSON o YAML):
```json
{
  "language": "Italian",
  "voice_description": "Voce femminile giovane, tono amichevole e energico",
  "output_format": "wav",
  "sample_rate": 24000
}
```

**Esempi di descrizioni vocali efficaci**:
- Italiano: "Voce maschile matura, tono professionale e rassicurante, ritmo moderato"
- English: "Young female voice, enthusiastic and friendly tone, clear articulation"

## Comandi Comuni

### Generazione Audio da File di Testo
```bash
# Script principale (da creare)
python src/generate_audio.py --input INPUT/testo.txt --config config/voice_config.json
```

### Elaborazione Batch
```bash
# Processa tutti i file in INPUT/
python src/batch_process.py --config config/voice_config.json
```

### Generazione Lezioni Biochimica (con preprocessing terminologia scientifica)
```bash
# Genera audio di lezione con pronuncia corretta di termini scientifici
python src/generate_biochem_lecture.py -i INPUT/biochemistry_sample.txt -o OUTPUT/lecture.wav

# Preview del preprocessing senza generare audio
python src/generate_biochem_lecture.py -i INPUT/file.txt -o dummy.wav --preview-preprocessing
```

**Nota**: Vedi `docs/BIOCHEMISTRY_TTS_GUIDE.md` per guida completa su generazione audio per lezioni scientifiche.

### Web UI Demo Locale (per testing)
```bash
qwen-tts-demo Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign --ip 0.0.0.0 --port 8000
# Aprire http://localhost:8000
```

## Ottimizzazioni per M3 Max

### Utilizzo Memoria
- **RAM Unificata**: 36GB sufficiente per modello 1.7B
- **Device**: Usare `device_map="mps"` per Metal Performance Shaders
- **Dtype**: `torch.bfloat16` per bilanciare qualità e prestazioni

### Parametri di Generazione
- `max_new_tokens=2048`: Default per generazione audio
- Batch processing: Processare 2-4 file contemporaneamente per ottimizzare uso GPU

## Lingue Supportate

Il modello supporta 10 lingue principali:
- Chinese, English, Japanese, Korean
- German, French, Russian, Portuguese, Spanish, Italian

**Nota**: Per migliore qualità, specificare esplicitamente `language` invece di usare "Auto".

## Conversione Formati Audio

### WAV → MP3
```python
from pydub import AudioSegment
audio = AudioSegment.from_wav("output.wav")
audio.export("output.mp3", format="mp3", bitrate="192k")
```

## Note Tecniche

### Tokenizer
- **Qwen3-TTS-Tokenizer-12Hz**: 12.5 fps, 16 codebook, 2048 codebook size
- Compressione acustica efficiente con alta fedeltà
- Preserva informazioni paralinguistiche

### Latenza
- Streaming generation supportato
- Prima generazione: ~1-2 secondi (caricamento modello)
- Generazioni successive: latenza minima in streaming mode

## TODO / Funzionalità Future

### Voice Cloning (da implementare)
- [ ] Configurare modello **Qwen3-TTS-12Hz-1.7B-VoiceClone** per clonazione vocale
- [ ] Creare script per voice cloning da campioni audio (3-10 secondi)
- [ ] Implementare cross-lingual voice cloning (es. voce inglese che parla italiano)
- [ ] Creare configurazioni JSON per gestire riferimenti audio per cloning
- [ ] Testare qualità cloning con diverse sorgenti audio

**Note Voice Cloning**:
```python
# Esempio uso futuro
model_clone = Qwen3TTSModel.from_pretrained(
    "Qwen/Qwen3-TTS-12Hz-1.7B-VoiceClone",
    device_map="mps",
    dtype=torch.bfloat16
)

wavs, sr = model_clone.generate_voice_clone(
    text="Testo da far pronunciare",
    language="Italian",
    prompt_speech="path/to/voice_sample.wav"  # 3-10 sec audio pulito
)
```

## Riferimenti

- **Paper**: https://arxiv.org/abs/2601.15621
- **Hugging Face**: https://huggingface.co/collections/Qwen/qwen3-tts
- **Blog**: https://qwen.ai/blog?id=qwen3tts-0115
- **Demo Online**: https://huggingface.co/spaces/Qwen/Qwen3-TTS
