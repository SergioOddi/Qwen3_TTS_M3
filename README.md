# TTS_M3 - Converti Testo in Audio

Sistema Text-to-Speech locale che converte file di testo in audio naturale. Basato su Qwen3-TTS, funziona al 100% offline su MacBook Pro M3 Max.

---

## 🚀 Guide Pratiche

📝 **[TESTO_IN_VOCE.md](TESTO_IN_VOCE.md)** - Converti testo in audio (2 passi)
🎙️ **[CLONAZIONE_VOCE.md](CLONAZIONE_VOCE.md)** - Clona una voce reale (3 passi)

---

## ⚡ Esempi Rapidi

### Converti Testo in Audio
```bash
echo "Benvenuto al sistema TTS" > INPUT/test.txt
python src/generate_audio.py -i INPUT/test.txt
```

### Usa Voce Clonata
```bash
# Voce Sermonti Narratore
python src/generate_cloned_audio.py -i INPUT/testo.txt -c config/sermonti_narratore.json

# Voce Gazzolo Docente
python src/generate_cloned_audio.py -i INPUT/testo.txt -c config/gazzolo_docente.json

# Voce Capone Narratore
python src/generate_cloned_audio.py -i INPUT/testo.txt -c config/capone_narratore.json
```






---

## 🚀 Installazione (3 Passi)

```bash
# 1. Clona il repository
git clone <repository-url>
cd TTS_M3

# 2. Esegui setup automatico
./scripts/setup.sh

# 3. Attiva ambiente
conda activate qwen3-tts
```

Il setup installa automaticamente tutte le dipendenze e scarica i modelli (~10GB).

---

## 📝 Utilizzo Base

### 1. Crea un file di testo

```bash
echo "Benvenuto al sistema di sintesi vocale. Questo è un test." > INPUT/mio_testo.txt
```

### 2. Genera l'audio

```bash
python src/generate_audio.py -i INPUT/mio_testo.txt
```

### 3. Trova l'audio generato

Il file audio sarà in `OUTPUT/mio_testo.wav`

**È così semplice!**

---

## 🎯 Elaborazione Batch

Converti tutti i file `.txt` nella cartella INPUT in un colpo solo:

```bash
# Processa tutti i file
python src/batch_process.py

# Con configurazione voce specifica
python src/batch_process.py -c config/voice_config_female.json
```

---

## 🎤 Configurazioni Voci Disponibili

Usa `-c config/nome_file.json` per personalizzare la voce:

### Voice Design (descrizione testuale)
- `voice_config.json` - Voce maschile italiana professionale (default)
- `voice_config_female.json` - Voce femminile italiana energica
- `voice_config_english.json` - Voce maschile inglese professionale
- `voice_config_narratore.json` - Voce narratore italiano

### Voice Cloning (da campione audio)
- `gazzolo.json` - Voce clonata di Gazzolo
- `gazzolo_docente.json` - Voce Gazzolo stile docente biochimica
- `capone.json` - Voce clonata di Capone
- `capone_docente.json` - Voce Capone stile docente biochimica
- `sermonti.json` - Voce clonata di Sermonti

**Voice Cloning**: Usa campioni audio in `VOICE_SAMPLES/` per clonare voci reali.

---

## 📚 Esempi Pratici

### Esempio 1: Generazione Semplice

```bash
# Crea testo
echo "La biochimica è lo studio delle reazioni chimiche negli organismi viventi." > INPUT/lezione.txt

# Genera con voce maschile italiana
python src/generate_audio.py -i INPUT/lezione.txt

# Output: OUTPUT/lezione.wav
```

### Esempio 2: Cambiare Voce

```bash
# Voce femminile
python src/generate_audio.py -i INPUT/lezione.txt -c config/voice_config_female.json

# Voce clonata (Gazzolo)
python src/generate_audio.py -i INPUT/lezione.txt -c config/gazzolo_docente.json

# Voce inglese
python src/generate_audio.py -i INPUT/testo_en.txt -c config/voice_config_english.json
```

### Esempio 3: Lezioni di Biochimica

```bash
# Usa preprocessor per termini scientifici + voce docente
python src/generate_biochem_lecture.py -i INPUT/biochimica.txt -c config/gazzolo_docente.json
```

Il preprocessor corregge automaticamente la pronuncia di termini come "ATP", "NADH", "enzima", ecc.

---

## 🔧 Personalizzare le Voci

### Voice Design (descrivi la voce che vuoi)

Crea un nuovo file in `config/mia_voce.json`:

```json
{
  "language": "Italian",
  "voice_description": "Voce maschile giovane, tono energico e amichevole, ritmo veloce",
  "output_format": "wav"
}
```

Poi usalo:
```bash
python src/generate_audio.py -i INPUT/testo.txt -c config/mia_voce.json
```

### Voice Cloning (clona una voce reale)

1. Metti un campione audio (5-10 secondi) in `VOICE_SAMPLES/mia_voce.wav`
2. Crea config `config/mia_voce.json`:

```json
{
  "mode": "voice_clone",
  "language": "Italian",
  "voice_name": "mia_voce",
  "prompt_speech_path": "VOICE_SAMPLES/mia_voce.wav",
  "ref_text": "Trascrizione esatta del campione audio",
  "output_format": "wav"
}
```

3. Usa:
```bash
python src/generate_cloned_audio.py -i INPUT/testo.txt -c config/mia_voce.json
```

---

## 📁 Struttura Progetto

```
TTS_M3/
├── INPUT/              # Metti qui i file .txt da convertire
├── OUTPUT/             # Trovi qui gli audio generati (.wav/.mp3)
├── config/             # Configurazioni voci (personalizza qui)
├── VOICE_SAMPLES/      # Campioni audio per voice cloning
├── src/                # Codice sorgente (non modificare)
├── scripts/            # Script di setup e utilità
├── docs/               # Documentazione completa
└── models/             # Cache modelli (auto-download)
```

---

## ⚡ Performance su M3 Max

- **Primo avvio**: ~10-20 secondi (download modelli)
- **Generazioni successive**: ~1-2 secondi per frase breve
- **Batch processing**: Riutilizza modelli caricati (molto veloce)
- **Uso RAM**: ~5-8GB (modello 1.7B + overhead)
- **100% offline**: Nessuna connessione internet richiesta dopo setup

---

## 🆘 Problemi Comuni

### Il modello non si scarica

```bash
# Download manuale
pip install -U modelscope
modelscope download --model Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign --local_dir ./models/Qwen3-TTS-12Hz-1.7B-VoiceDesign
```

### Conversione MP3 fallisce

```bash
# Installa ffmpeg
brew install ffmpeg
```

### Errore "device_map"

Se hai problemi con GPU, modifica `src/generate_audio.py` e cambia `device_map="mps"` in `device_map="cpu"`.

---

## 📖 Documentazione Completa

### Guide Pratiche (⭐ Inizia da qui)
- **[TESTO_IN_VOCE.md](TESTO_IN_VOCE.md)** - Come convertire testo in audio
- **[CLONAZIONE_VOCE.md](CLONAZIONE_VOCE.md)** - Come clonare una voce

### Documentazione Dettagliata
- [CLAUDE.md](CLAUDE.md) - Istruzioni tecniche per sviluppatori
- [docs/QUICKSTART.md](docs/QUICKSTART.md) - Guida rapida
- [docs/EXAMPLES.md](docs/EXAMPLES.md) - Esempi avanzati
- [docs/BIOCHEMISTRY_TTS_GUIDE.md](docs/BIOCHEMISTRY_TTS_GUIDE.md) - Lezioni scientifiche
- [docs/VOICE_CLONING_GUIDE.md](docs/VOICE_CLONING_GUIDE.md) - Voice cloning dettagliato
- [docs/VOCI_DISPONIBILI.md](docs/VOCI_DISPONIBILI.md) - Catalogo voci clonate
- [config/README.md](config/README.md) - Configurazioni voci

---

## 🌍 Lingue Supportate

🇮🇹 Italiano | 🇬🇧 Inglese | 🇪🇸 Spagnolo | 🇫🇷 Francese | 🇩🇪 Tedesco
🇵🇹 Portoghese | 🇷🇺 Russo | 🇨🇳 Cinese | 🇯🇵 Giapponese | 🇰🇷 Coreano

**Nota**: Specifica sempre la lingua nel file di configurazione per miglior qualità.

---

## 🔗 Riferimenti

- **Paper**: [Qwen3-TTS Technical Report](https://arxiv.org/abs/2601.15621)
- **Hugging Face**: [Qwen3-TTS Collection](https://huggingface.co/collections/Qwen/qwen3-tts)
- **Demo Online**: [Qwen3-TTS Space](https://huggingface.co/spaces/Qwen/Qwen3-TTS)

---

**Sviluppato per MacBook Pro M3 Max | Powered by Qwen3-TTS**
