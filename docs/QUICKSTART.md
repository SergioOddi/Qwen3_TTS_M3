# Guida Rapida - TTS_M3

Inizia subito a generare audio con Qwen3-TTS in 3 semplici passi.

## ⚡ Setup Veloce (5 minuti)

### 1. Installa l'ambiente

```bash
./setup.sh
```

Lo script farà tutto automaticamente:
- Crea ambiente conda `qwen3-tts`
- Installa tutte le dipendenze
- Configura ottimizzazioni M3 Max
- Verifica installazione

### 2. Attiva l'ambiente

```bash
conda activate qwen3-tts
```

### 3. Test rapido

```bash
# Verifica installazione
python test_installation.py

# Genera primo audio
python src/generate_audio.py -i INPUT/esempio.txt
```

Il file audio sarà in `OUTPUT/esempio.wav`

## 🎯 Utilizzo Base

### File Singolo

```bash
# Crea il tuo testo
echo "Il tuo testo qui" > INPUT/mio_testo.txt

# Genera audio
python src/generate_audio.py -i INPUT/mio_testo.txt

# Risultato: OUTPUT/mio_testo.wav
```

### Multipli File (Batch)

```bash
# Aggiungi più file .txt in INPUT/
echo "Primo testo" > INPUT/file1.txt
echo "Secondo testo" > INPUT/file2.txt

# Processa tutto
python src/batch_process.py

# Risultati: OUTPUT/file1.wav, OUTPUT/file2.wav
```

## 🎤 Cambiare Voce

### Voce Femminile

```bash
python src/generate_audio.py \
  -i INPUT/testo.txt \
  -c config/voice_config_female.json
```

### Voce Inglese

```bash
python src/generate_audio.py \
  -i INPUT/text.txt \
  -c config/voice_config_english.json
```

### Voce Personalizzata

Modifica `config/voice_config.json`:

```json
{
  "language": "Italian",
  "voice_description": "La tua descrizione qui: es. voce anziana, tono saggio, ritmo lento",
  "output_format": "wav"
}
```

## 💡 Tips Utili

### Output MP3 invece di WAV

In `config/voice_config.json`:

```json
{
  "output_format": "mp3"
}
```

**Richiede**: `ffmpeg` installato (`brew install ffmpeg`)

### Specificare Output Manualmente

```bash
python src/generate_audio.py \
  -i INPUT/testo.txt \
  -o OUTPUT/nome_custom.wav
```

### Rigenerare File Esistenti (Batch)

```bash
# Normalmente salta file già generati
python src/batch_process.py

# Forza rigenerazione
python src/batch_process.py --force
```

## 📚 Workflow Tipici

### Audiolibro

```bash
# 1. Prepara capitoli in INPUT/
# capitolo_01.txt, capitolo_02.txt, ...

# 2. Genera tutto in batch
python src/batch_process.py

# 3. Trova audio in OUTPUT/
# capitolo_01.wav, capitolo_02.wav, ...
```

### Podcast con Voci Multiple

```bash
# Host (maschio)
python src/generate_audio.py \
  -i INPUT/intro_host.txt \
  -c config/voice_config.json \
  -o OUTPUT/01_intro.wav

# Ospite (femmina)
python src/generate_audio.py \
  -i INPUT/intervista_ospite.txt \
  -c config/voice_config_female.json \
  -o OUTPUT/02_intervista.wav
```

### Contenuto Multilingua

```bash
# Parte italiana
python src/generate_audio.py \
  -i INPUT/parte_italiana.txt \
  -c config/voice_config.json

# Parte inglese
python src/generate_audio.py \
  -i INPUT/english_part.txt \
  -c config/voice_config_english.json
```

## ⚙️ Comandi Utili

### Verifica Ambiente

```bash
python test_installation.py
```

### Help Script

```bash
python src/generate_audio.py --help
python src/batch_process.py --help
```

### Demo Web (Testing)

```bash
qwen-tts-demo Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign --port 8000
# Apri http://localhost:8000
```

## 🔧 Risoluzione Problemi Comuni

### "ModuleNotFoundError: No module named 'qwen_tts'"

```bash
# Verifica ambiente attivo
conda activate qwen3-tts

# Reinstalla
pip install -U qwen-tts
```

### "File di configurazione non trovato"

```bash
# Verifica esistenza
ls config/voice_config.json

# Se mancante, ricrea da README
```

### Generazione lenta

Prima generazione è più lenta (download modello):
- Prima volta: ~10-20 sec
- Successive: ~1-2 sec

Per velocizzare batch, usa `batch_process.py` che riusa il modello.

### Errore MPS (Metal)

Se hai problemi GPU, modifica `src/generate_audio.py`:

```python
device_map="cpu"  # invece di "mps"
```

## 📖 Prossimi Passi

1. ✅ Setup completato
2. ✅ Primo audio generato
3. 📚 Leggi [README.md](README.md) per dettagli completi
4. 🎤 Esplora [config/README.md](config/README.md) per voice design
5. 🔧 Consulta [CLAUDE.md](CLAUDE.md) per dettagli tecnici

## 🆘 Supporto

Se qualcosa non funziona:

1. Esegui `python test_installation.py` per diagnosticare
2. Verifica messaggi di errore
3. Consulta sezione "Risoluzione Problemi" in README.md
4. Verifica documentazione tecnica in CLAUDE.md

---

**Happy TTS! 🎵**
