# Guida Completa Voice Cloning con Qwen3-TTS

Questa guida spiega come clonare voci usando il modello Qwen3-TTS-12Hz-1.7B-Base.

## Indice
1. [Quick Start](#quick-start)
2. [Preparazione Campioni Vocali](#preparazione-campioni-vocali)
3. [Configurazione](#configurazione)
4. [Utilizzo Script](#utilizzo-script)
5. [Best Practices](#best-practices)
6. [Cross-Lingual Cloning](#cross-lingual-cloning)
7. [Troubleshooting](#troubleshooting)

---

## Quick Start

### 1. Estrai audio da video MP4
```bash
python src/extract_audio_from_video.py -i mio_video.mp4 -o VOICE_SAMPLES/mia_voce.wav --start 5 --duration 5
```

### 2. Crea file di configurazione
```bash
cp config/clone_config_template.json config/clone_config_mia_voce.json
# Edita config/clone_config_mia_voce.json:
#   "prompt_speech_path": "VOICE_SAMPLES/mia_voce.wav"
```

### 3. Genera audio clonato
```bash
python src/generate_cloned_audio.py -i INPUT/testo.txt -c config/clone_config_mia_voce.json -o OUTPUT/audio_clonato.wav
```

---

## Preparazione Campioni Vocali

### Caratteristiche Ottimali

**Durata:**
- ✓ **Ottimale**: 5-7 secondi
- ⚠ Accettabile: 3-10 secondi
- ✗ Sconsigliato: < 3 secondi o > 15 secondi

**Formato Audio:**
- ✓ **Ottimale**: WAV mono 24kHz
- ⚠ Accettabile: MP3 >= 128kbps, stereo, >= 16kHz
- ✗ Sconsigliato: Formati lossy a basso bitrate

**Qualità Registrazione:**
- ✓ Voce chiara senza rumori di fondo
- ✓ Volume normale (non sussurrato o urlato)
- ✓ Pronuncia naturale
- ✗ Evitare: Eco, rumori ambientali, distorsioni

### Fonti Audio Consigliate

**Ottime:**
- Registrazioni in studio
- Audio estratti da video interviste professionali
- Podcast con buona qualità audio
- Audiobook

**Accettabili:**
- Video YouTube di buona qualità
- Registrazioni da smartphone in ambiente silenzioso
- Chiamate vocali pulite

**Da evitare:**
- Audio con musica di sottofondo
- Registrazioni con eco o riverbero marcato
- Audio con compressione pesante
- Voci sintetiche o processate

### Estrazione da Video MP4

#### Estrazione Base
```bash
# Estrai tutto l'audio
python src/extract_audio_from_video.py -i video.mp4 -o VOICE_SAMPLES/voice.wav
```

#### Estrazione con Ritaglio Temporale
```bash
# Estrai 5 secondi partendo dal secondo 10
python src/extract_audio_from_video.py -i video.mp4 -o VOICE_SAMPLES/voice.wav --start 10 --duration 5

# Trova il momento migliore nel video:
# 1. Apri video in QuickTime/VLC
# 2. Trova segmento con voce chiara (5-7 secondi)
# 3. Annota timestamp inizio (es. 00:01:23 = 83 secondi)
# 4. Estrai quel segmento:
python src/extract_audio_from_video.py -i video.mp4 -o VOICE_SAMPLES/voice.wav --start 83 --duration 6
```

#### Batch Processing da Cartella
```bash
# Estrai audio da tutti i video in una cartella
python src/extract_audio_from_video.py -i videos/ -o VOICE_SAMPLES/extracted/
```

### Preparazione Campione Ottimale

Lo script `prepare_voice_sample.py` ottimizza automaticamente il campione:

```bash
# Normalizza volume e rimuovi silenzio
python src/prepare_voice_sample.py -i VOICE_SAMPLES/raw.wav -o VOICE_SAMPLES/speaker_clean.wav

# Estrai segmento specifico + ottimizzazione
python src/prepare_voice_sample.py -i audio.mp3 -o VOICE_SAMPLES/speaker.wav --start 10 --duration 5

# Suggerisci miglior segmento
python src/prepare_voice_sample.py -i audio.mp3 --suggest
```

**Cosa fa lo script:**
- Rimuove silenzio iniziale/finale
- Normalizza volume a -16 LUFS
- Converte a WAV mono 24kHz
- Verifica durata ottimale

### Lista Campioni Disponibili

```bash
# Lista tutti i campioni in VOICE_SAMPLES/
python src/list_voice_samples.py

# Output esempio:
# 1. ✓ speaker1.wav
#    Durata: 5.2s | Sample rate: 24.0kHz | Canali: mono | Size: 0.25 MB
# 2. ⚠ speaker2.mp3
#    Durata: 12.5s | Sample rate: 44.1kHz | Canali: stereo | Size: 1.2 MB
#    💡 Suggerimento: Durata > 10s. Considera di ritagliare a 5-8s
```

---

## Configurazione

### Struttura File JSON

```json
{
  "mode": "voice_clone",
  "language": "Italian",
  "prompt_speech_path": "VOICE_SAMPLES/speaker.wav",
  "output_format": "wav",
  "sample_rate": 24000,
  "voice_notes": "Descrizione opzionale del campione"
}
```

### Parametri

- **`mode`**: Sempre `"voice_clone"` per voice cloning
- **`language`**: Lingua target output (`"Italian"`, `"English"`, etc.)
- **`prompt_speech_path`**: Path relativo al campione audio
- **`output_format`**: `"wav"` (raccomandato) o `"mp3"`
- **`sample_rate`**: Sample rate output (default 24000)
- **`voice_notes`**: Note descrittive (opzionale)

### Configurazioni Predefinite

Il repository include questi template:

#### `clone_config_template.json`
Template base da copiare e personalizzare.

#### `clone_config_speaker1.json`
```json
{
  "mode": "voice_clone",
  "language": "Italian",
  "prompt_speech_path": "VOICE_SAMPLES/speaker1.wav",
  "output_format": "wav",
  "sample_rate": 24000,
  "voice_notes": "Voce maschile italiana, tono professionale"
}
```

#### `clone_config_cross_lingual.json`
```json
{
  "mode": "voice_clone",
  "language": "Italian",
  "prompt_speech_path": "VOICE_SAMPLES/english_speaker.wav",
  "output_format": "wav",
  "sample_rate": 24000,
  "voice_notes": "Cross-lingual: voce inglese per sintetizzare italiano"
}
```

---

## Utilizzo Script

### Generazione Singolo File

```bash
python src/generate_cloned_audio.py -i INPUT/testo.txt -c config/clone_config_speaker1.json -o OUTPUT/cloned.wav
```

**Parametri:**
- `-i, --input`: File .txt con testo da sintetizzare (richiesto)
- `-c, --config`: File configurazione JSON (richiesto)
- `-o, --output`: File audio output (default: `OUTPUT/[nome]_cloned.wav`)
- `--use-biochem-preprocessor`: Applica preprocessing terminologia scientifica
- `--preview-preprocessing`: Mostra preview preprocessing senza generare audio

**Esempi:**
```bash
# Base
python src/generate_cloned_audio.py -i INPUT/lezione.txt -c config/clone_config.json

# Con preprocessing biochimica
python src/generate_cloned_audio.py -i INPUT/biochemistry.txt -c config/clone_config.json --use-biochem-preprocessor

# Preview preprocessing
python src/generate_cloned_audio.py -i INPUT/biochemistry.txt -c config/clone_config.json --preview-preprocessing
```

### Batch Processing

Processa tutti i file .txt in INPUT/:

```bash
python src/batch_clone_process.py -c config/clone_config_speaker1.json
```

**Parametri:**
- `-c, --config`: File configurazione JSON (richiesto)
- `-i, --input`: Directory input (default: `INPUT`)
- `-o, --output`: Directory output (default: `OUTPUT`)
- `-f, --force`: Rigenera file già esistenti
- `--use-biochem-preprocessor`: Applica preprocessing biochimica

**Esempi:**
```bash
# Batch base
python src/batch_clone_process.py -c config/clone_config.json

# Directory custom
python src/batch_clone_process.py -i MY_TEXTS/ -o MY_OUTPUT/ -c config/clone_config.json

# Rigenera tutto
python src/batch_clone_process.py -c config/clone_config.json --force

# Con preprocessing biochimica
python src/batch_clone_process.py -c config/clone_config.json --use-biochem-preprocessor
```

**Note:**
- Il modello viene caricato **una sola volta** all'inizio
- File output hanno suffisso `_cloned` per distinguerli
- File esistenti vengono saltati (usa `--force` per rigenerare)

---

## Best Practices

### 1. Scelta Campione Vocale

✓ **Raccomandato:**
- Voce naturale e rilassata
- Pronuncia chiara
- Volume uniforme
- Assenza rumori di fondo
- 5-7 secondi di durata

✗ **Evitare:**
- Voce sussurrata o urlata
- Pronuncia forzata o enfatizzata
- Audio con eco/riverbero
- Segmenti con risate, colpi di tosse
- Durata < 3s o > 15s

### 2. Qualità Audio Source

**Priorità:**
1. **Audio pulito** > risoluzione alta
2. **Mono** > stereo (per cloning)
3. **24kHz** > frequenze più alte (balance qualità/performance)

**Verifica qualità:**
```bash
python src/list_voice_samples.py --details
```

### 3. Ottimizzazione Performance

**Su M3 Max (36GB RAM):**
- Batch processing: 2-4 file contemporanei ottimale
- Usa Flash Attention 2 se disponibile
- `device_map="mps"` per Metal Performance Shaders
- `dtype=torch.bfloat16` per balance qualità/performance

### 4. Gestione Voci Multiple

**Organizzazione:**
```
VOICE_SAMPLES/
├── narratore_uomo.wav
├── narratore_donna.wav
├── studente_voce.wav
└── professore_voce.wav

config/
├── clone_narratore_uomo.json
├── clone_narratore_donna.json
├── clone_studente.json
└── clone_professore.json
```

**Workflow:**
```bash
# Usa configurazioni diverse per voci diverse
python src/generate_cloned_audio.py -i testo1.txt -c config/clone_narratore_uomo.json
python src/generate_cloned_audio.py -i testo2.txt -c config/clone_narratore_donna.json
```

---

## Cross-Lingual Cloning

Il modello supporta **cross-lingual cloning**: clonare voce da una lingua e sintetizzare in un'altra.

### Esempio: Voce Inglese → Testo Italiano

**1. Prepara campione voce inglese:**
```bash
python src/extract_audio_from_video.py -i english_video.mp4 -o VOICE_SAMPLES/english_speaker.wav --start 10 --duration 5
```

**2. Configurazione cross-lingual:**
```json
{
  "mode": "voice_clone",
  "language": "Italian",
  "prompt_speech_path": "VOICE_SAMPLES/english_speaker.wav",
  "output_format": "wav",
  "voice_notes": "Cross-lingual: voce inglese per italiano"
}
```

**3. Genera audio italiano con voce inglese:**
```bash
python src/generate_cloned_audio.py -i INPUT/testo_italiano.txt -c config/clone_cross_lingual.json
```

### Note Cross-Lingual

✓ **Vantaggi:**
- Mantiene caratteristiche timbriche (tono, intonazione)
- Funziona tra tutte le 10 lingue supportate
- Utile per contenuti multilingue

⚠ **Limitazioni:**
- Qualità leggermente inferiore vs. same-language cloning
- Accento potrebbe essere meno naturale
- Raccomandato testare prima con campioni brevi

**Lingue supportate:**
Chinese, English, Japanese, Korean, German, French, Russian, Portuguese, Spanish, Italian

---

## Troubleshooting

### Problema: "Errore: Campione audio non trovato"

**Causa:** Path errato in configurazione JSON.

**Soluzione:**
```bash
# Verifica path campioni disponibili
python src/list_voice_samples.py

# Correggi "prompt_speech_path" in config JSON
# Usa path relativo dalla root del progetto:
"prompt_speech_path": "VOICE_SAMPLES/speaker.wav"  ✓
"prompt_speech_path": "/full/path/speaker.wav"     ✗ (evitare path assoluti)
```

### Problema: "Audio generato ha qualità scadente"

**Possibili cause e soluzioni:**

1. **Campione troppo corto (< 3s)**
   ```bash
   python src/list_voice_samples.py  # Verifica durata
   # Soluzione: Usa campione più lungo (5-7s)
   ```

2. **Audio source con rumori**
   ```bash
   # Prepara campione pulito
   python src/prepare_voice_sample.py -i noisy.wav -o clean.wav
   ```

3. **Cross-lingual con lingue molto diverse**
   - Soluzione: Usa same-language cloning quando possibile

### Problema: "Modello scarica lentamente o timeout"

**Causa:** Primo download modello Base (~3.4GB).

**Soluzione:**
```bash
# Download manuale con modelscope
pip install -U modelscope
modelscope download --model Qwen/Qwen3-TTS-12Hz-1.7B-Base --local_dir ./models/Qwen3-TTS-12Hz-1.7B-Base

# Poi usa nel codice:
model = Qwen3TTSModel.from_pretrained(
    "./models/Qwen3-TTS-12Hz-1.7B-Base",  # Path locale
    device_map="mps",
    dtype=torch.bfloat16
)
```

### Problema: "Errore: ffmpeg non trovato"

**Causa:** ffmpeg non installato.

**Soluzione:**
```bash
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt install ffmpeg

# Verifica installazione
ffmpeg -version
```

### Problema: "Flash Attention 2 non disponibile"

**Causa:** Flash Attention 2 non installato o incompatibile.

**Impatto:** Nessun problema critico. Lo script usa automaticamente fallback standard.

**Soluzione (opzionale):**
```bash
# Installazione Flash Attention 2 su M3 Max
MAX_JOBS=4 pip install -U flash-attn --no-build-isolation
```

### Problema: "Out of memory durante batch processing"

**Causa:** Troppi file processati contemporaneamente.

**Soluzione:**
```bash
# Riduci numero file in INPUT/
# Oppure aumenta RAM disponibile chiudendo altre app
# Oppure processa in lotti più piccoli
```

### Problema: "Voce clonata suona robotica"

**Possibili cause:**
1. Campione source di bassa qualità
2. Campione troppo corto
3. Testo target molto diverso da source

**Soluzione:**
- Usa campione pulito 5-7s
- Verifica qualità con `list_voice_samples.py`
- Testa con testo simile a quello del campione

---

## Risorse Aggiuntive

- **Documentazione principale:** `CLAUDE.md`
- **Esempi pratici:** `EXAMPLES.md`
- **Guida biochimica:** `docs/BIOCHEMISTRY_TTS_GUIDE.md`
- **Paper Qwen3-TTS:** https://arxiv.org/abs/2601.15621
- **Demo online:** https://huggingface.co/spaces/Qwen/Qwen3-TTS

---

**Versione:** 1.0
**Data:** Febbraio 2026
**Compatibile con:** Qwen3-TTS v0.0.5+, Python 3.12, macOS (M3 Max)
