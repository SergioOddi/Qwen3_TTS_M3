# 🎙️ Clonazione Voce - Guida Pratica

Questa guida ti spiega come clonare una voce in 3 semplici passi.

---

## ⚡ Quick Start (3 passi)

### 1️⃣ Prepara un Campione Audio (5-7 secondi)

#### Opzione A: Estrai da Video MP4
```bash
python src/extract_audio_from_video.py -i video.mp4 -o VOICE_SAMPLES/mia_voce.wav --start 10 --duration 5
```
- `--start 10`: Inizia dal secondo 10
- `--duration 5`: Estrai 5 secondi

#### Opzione B: Copia File Audio Esistente
```bash
cp ~/Downloads/audio.wav VOICE_SAMPLES/mia_voce.wav
```

#### Verifica il Campione
```bash
python src/list_voice_samples.py
```

---

### 2️⃣ Trascrivi l'Audio

**IMPORTANTE**: Ascolta il campione e scrivi ESATTAMENTE cosa viene detto.

Esempio:
- Audio dice: *"Buongiorno, oggi parliamo di biochimica"*
- Trascrizione: `"Buongiorno, oggi parliamo di biochimica"`

---

### 3️⃣ Crea File di Configurazione

Crea un file JSON in `config/mia_voce.json`:

```json
{
  "mode": "voice_clone",
  "language": "Italian",
  "voice_name": "mia_voce",
  "prompt_speech_path": "VOICE_SAMPLES/mia_voce.wav",
  "ref_text": "Buongiorno, oggi parliamo di biochimica",
  "output_format": "wav",
  "sample_rate": 24000
}
```

**Campi da personalizzare:**
- `voice_name`: Nome della voce (es. "mario", "gazzolo", "narratore")
- `prompt_speech_path`: Path al file audio
- `ref_text`: Trascrizione ESATTA dell'audio

---

## 🚀 Utilizzo

### Genera Audio da un Testo

```bash
python src/generate_cloned_audio.py -i INPUT/testo.txt -c config/mia_voce.json
```

Il file audio sarà in: `OUTPUT/testo_by_mia_voce.wav`

### Elabora Tutti i File in INPUT/

```bash
python src/batch_clone_process.py -c config/mia_voce.json
```

---

## 📁 Esempio Completo

### 1. Ho un video `intervista.mp4` e voglio clonare la voce

```bash
# Estrai 6 secondi dal secondo 15
python src/extract_audio_from_video.py -i intervista.mp4 -o VOICE_SAMPLES/speaker.wav --start 15 --duration 6
```

### 2. Ascolto l'audio e trascrivo

Audio dice: *"La sintesi proteica è un processo fondamentale della cellula"*

### 3. Creo `config/speaker.json`

```json
{
  "mode": "voice_clone",
  "language": "Italian",
  "voice_name": "speaker",
  "prompt_speech_path": "VOICE_SAMPLES/speaker.wav",
  "ref_text": "La sintesi proteica è un processo fondamentale della cellula",
  "output_format": "wav"
}
```

### 4. Creo un testo da far leggere

```bash
echo "Benvenuti alla lezione di oggi sulla biochimica cellulare." > INPUT/lezione.txt
```

### 5. Genero l'audio con la voce clonata

```bash
python src/generate_cloned_audio.py -i INPUT/lezione.txt -c config/speaker.json
```

**Output**: `OUTPUT/lezione_by_speaker.wav`

---

## 💡 Consigli per Campioni di Qualità

### ✅ Campione BUONO
- Durata: 5-7 secondi
- Audio pulito senza rumori
- Voce naturale e chiara
- Pronuncia normale (né sussurrata né urlata)

### ❌ Campione SCADENTE
- Troppo corto (< 3 secondi)
- Rumori di fondo, musica
- Audio con eco o riverbero
- Voce distorta o compressa male

### 🔍 Dove Trovare Buoni Campioni
- ✅ Video interviste professionali
- ✅ Podcast con audio pulito
- ✅ Registrazioni in studio
- ✅ Audiolibri
- ❌ Video con musica di sottofondo
- ❌ Chiamate telefoniche rumorose

---

## 🎯 Voci Clonate Disponibili

Il progetto include già alcune voci pronte all'uso:

| Voce | Configurazione | Ideale per |
|------|---------------|------------|
| Gazzolo | `config/gazzolo.json` | Narrazione naturale |
| Gazzolo Docente | `config/gazzolo_docente.json` | Lezioni biochimica |
| Capone | `config/capone.json` | Narrazione generale |
| Capone Docente | `config/capone_docente.json` | Contenuti didattici |
| Sermonti | `config/sermonti.json` | Narrazione classica |
| Sermonti Narratore | `config/sermonti_narratore.json` | Storytelling |

### Esempio con Voci Esistenti

```bash
# Usa voce Gazzolo
python src/generate_cloned_audio.py -i INPUT/testo.txt -c config/gazzolo.json

# Usa voce Capone Docente
python src/generate_cloned_audio.py -i INPUT/lezione.txt -c config/capone_docente.json
```

---

## 🔧 Funzioni Avanzate

### Ottimizza Campione Audio

```bash
# Normalizza volume e rimuovi silenzi
python src/prepare_voice_sample.py -i VOICE_SAMPLES/raw.wav -o VOICE_SAMPLES/clean.wav
```

### Trova il Miglior Segmento

```bash
# Analizza audio lungo e suggerisce segmento ottimale
python src/prepare_voice_sample.py -i audio_lungo.mp3 --suggest
```

### Batch Processing Completo

```bash
# Processa tutti i .txt in INPUT/ con stessa voce
python src/batch_clone_process.py -c config/mia_voce.json

# Rigenera anche file esistenti
python src/batch_clone_process.py -c config/mia_voce.json --force
```

### Lezioni Scientifiche

```bash
# Usa preprocessor per termini scientifici
python src/generate_cloned_audio.py -i INPUT/biochimica.txt -c config/gazzolo_docente.json --use-biochem-preprocessor
```

---

## 🌍 Clonazione Multi-Lingua

Puoi clonare una voce in una lingua e farla parlare in un'altra.

### Esempio: Voce Inglese → Testo Italiano

```json
{
  "mode": "voice_clone",
  "language": "Italian",
  "voice_name": "english_speaker",
  "prompt_speech_path": "VOICE_SAMPLES/english_voice.wav",
  "ref_text": "Hello, this is a sample of my voice",
  "output_format": "wav"
}
```

```bash
python src/generate_cloned_audio.py -i INPUT/testo_italiano.txt -c config/english_speaker.json
```

**Nota**: La qualità è leggermente inferiore rispetto a same-language cloning.

---

## ❓ Problemi Comuni

### Audio non trovato
```bash
# Verifica path
python src/list_voice_samples.py
```
Correggi `prompt_speech_path` nel file JSON.

### Qualità scadente
- Verifica durata campione (5-7 secondi ottimale)
- Usa audio pulito senza rumori
- Evita campioni troppo corti (< 3s)

### Voce robotica
- Migliora qualità campione source
- Usa campione più lungo (6-7 secondi)
- Verifica trascrizione `ref_text` sia esatta

---

## 📚 Documentazione Completa

- [docs/VOICE_CLONING_GUIDE.md](docs/VOICE_CLONING_GUIDE.md) - Guida dettagliata
- [docs/VOCI_DISPONIBILI.md](docs/VOCI_DISPONIBILI.md) - Catalogo voci
- [CLAUDE.md](CLAUDE.md) - Documentazione tecnica

---

**Sviluppato per MacBook Pro M3 Max | Powered by Qwen3-TTS**
