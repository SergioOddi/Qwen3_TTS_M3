# TTS_M3 - Sistema Text-to-Speech Locale

Sistema TTS (Text-to-Speech) locale basato su **Qwen3-TTS** ottimizzato per MacBook Pro M3 Max. Genera voci naturali in italiano e inglese (e altre 8 lingue) usando il modello Qwen3-TTS-12Hz-1.7B-VoiceDesign.

## Caratteristiche

- 🎤 **Voice Design**: Controllo vocale tramite descrizioni testuali
- 🇮🇹 **Multilingua**: Supporto per 10 lingue (Italiano, Inglese, e altri)
- 🚀 **Ottimizzato M3**: Usa Metal Performance Shaders per massime prestazioni
- 📦 **Elaborazione Batch**: Processa multipli file automaticamente
- 🎵 **Formati multipli**: Output in WAV o MP3
- 💻 **100% Locale**: Nessuna connessione cloud richiesta

## Requisiti

- macOS (ottimizzato per M3 Max con 36GB RAM)
- Python 3.12
- Conda (Miniconda o Anaconda)
- ~10GB spazio disco (per modelli)

## Installazione Rapida

### 1. Clone repository
```bash
git clone <repository-url>
cd TTS_M3
```

### 2. Setup automatico
```bash
./setup.sh
```

Lo script di setup:
- Crea ambiente conda `qwen3-tts`
- Installa tutte le dipendenze
- Configura Flash Attention 2 (opzionale)
- Verifica installazione ffmpeg
- Esegue test di verifica

### 3. Setup manuale (alternativo)

Se preferisci installare manualmente:

```bash
# Crea ambiente
conda create -n qwen3-tts python=3.12 -y
conda activate qwen3-tts

# Installa dipendenze
pip install -r requirements.txt

# (Opzionale) Flash Attention 2 per migliori performance
MAX_JOBS=4 pip install -U flash-attn --no-build-isolation

# (Opzionale) ffmpeg per conversione MP3
brew install ffmpeg
```

## Utilizzo

### Generazione Singola

```bash
# Attiva ambiente
conda activate qwen3-tts

# Crea file di testo
echo "Benvenuto al sistema di sintesi vocale Qwen3-TTS." > INPUT/esempio.txt

# Genera audio
python src/generate_audio.py -i INPUT/esempio.txt

# Output: OUTPUT/esempio.wav
```

### Con Configurazione Custom

```bash
# Usa voce femminile
python src/generate_audio.py \
  -i INPUT/testo.txt \
  -c config/voice_config_female.json

# Specifica output
python src/generate_audio.py \
  -i INPUT/testo.txt \
  -o OUTPUT/mio_audio.wav \
  -c config/voice_config.json
```

### Elaborazione Batch

```bash
# Processa tutti i file .txt in INPUT/
python src/batch_process.py

# Con configurazione specifica
python src/batch_process.py -c config/voice_config_english.json

# Forza rigenerazione (sovrascrive esistenti)
python src/batch_process.py --force
```

## Configurazione Voci

I file di configurazione si trovano in `config/` e permettono di personalizzare:

- **Lingua**: Italian, English, Chinese, Japanese, etc.
- **Descrizione vocale**: Età, genere, tono, velocità
- **Formato output**: WAV o MP3
- **Sample rate**: Default 24kHz

### Esempio configurazione

```json
{
  "language": "Italian",
  "voice_description": "Voce maschile matura, tono professionale e rassicurante, ritmo moderato",
  "output_format": "wav",
  "sample_rate": 24000
}
```

### Configurazioni Pre-installate

- `voice_config.json`: Voce maschile italiana professionale
- `voice_config_female.json`: Voce femminile italiana energica
- `voice_config_english.json`: Voce maschile inglese professionale

Consulta [config/README.md](config/README.md) per esempi dettagliati di voice descriptions.

## Struttura Progetto

```
TTS_M3/
├── INPUT/                          # File .txt da convertire
│   └── esempio.txt
├── OUTPUT/                         # File audio generati
│   └── esempio.wav
├── config/                         # Configurazioni vocali
│   ├── voice_config.json          # Default (maschio IT)
│   ├── voice_config_female.json   # Femmina IT
│   ├── voice_config_english.json  # Maschio EN
│   └── README.md                  # Guida configurazioni
├── src/                           # Codice sorgente
│   ├── generate_audio.py         # Generazione singola
│   └── batch_process.py           # Elaborazione batch
├── models/                        # Cache modelli (auto-download)
├── requirements.txt               # Dipendenze Python
├── setup.sh                       # Script di setup
├── CLAUDE.md                      # Documentazione tecnica
└── README.md                      # Questo file
```

## Esempi di Utilizzo

### Esempio 1: Audiobook

```bash
# Prepara capitoli
echo "Capitolo 1: L'inizio..." > INPUT/capitolo_1.txt
echo "Capitolo 2: Lo sviluppo..." > INPUT/capitolo_2.txt

# Genera tutti i capitoli
python src/batch_process.py
```

### Esempio 2: Voci Multiple

```bash
# Narratore principale (maschio)
python src/generate_audio.py \
  -i INPUT/narrazione.txt \
  -c config/voice_config.json

# Dialogo personaggio (femmina)
python src/generate_audio.py \
  -i INPUT/dialogo.txt \
  -c config/voice_config_female.json
```

### Esempio 3: Contenuto Multilingua

```bash
# Testo italiano
python src/generate_audio.py \
  -i INPUT/testo_it.txt \
  -c config/voice_config.json

# Testo inglese
python src/generate_audio.py \
  -i INPUT/text_en.txt \
  -c config/voice_config_english.json
```

## Ottimizzazioni M3 Max

Il sistema è ottimizzato per M3 Max:

- **Metal Performance Shaders (MPS)**: Usa GPU integrata
- **RAM Unificata**: Sfrutta i 36GB per caricamento rapido
- **Flash Attention 2**: Riduce latenza e uso memoria
- **Batch Processing**: Elabora 2-4 file in parallelo

### Performance Attese

- Primo caricamento: ~10-20 secondi (download + init modello)
- Generazioni successive: ~1-2 secondi per frase breve
- Batch: Riusa modello caricato per massima efficienza

## Risoluzione Problemi

### Modello non si scarica

```bash
# Download manuale
pip install -U modelscope
modelscope download --model Qwen/Qwen3-TTS-Tokenizer-12Hz --local_dir ./models/Qwen3-TTS-Tokenizer-12Hz
modelscope download --model Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign --local_dir ./models/Qwen3-TTS-12Hz-1.7B-VoiceDesign
```

### Flash Attention 2 non si installa

Non è critico. Il sistema funziona anche senza:

```python
# Il codice fa fallback automatico all'implementazione standard
model = Qwen3TTSModel.from_pretrained(
    "Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign",
    device_map="mps",
    dtype=torch.bfloat16,
    # attn_implementation viene ignorato se FA2 non disponibile
)
```

### Conversione MP3 fallisce

Verifica installazione ffmpeg:

```bash
# macOS
brew install ffmpeg

# Verifica
ffmpeg -version
```

### Errore MPS (Metal)

Se hai problemi con MPS, usa CPU:

```python
# In generate_audio.py, modifica:
device_map="cpu"  # invece di "mps"
```

## Demo Web (Testing)

Per testare rapidamente il modello:

```bash
conda activate qwen3-tts
qwen-tts-demo Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign --ip 0.0.0.0 --port 8000
```

Apri http://localhost:8000 nel browser.

## Lingue Supportate

Il modello Qwen3-TTS supporta 10 lingue:

- 🇮🇹 Italian (Italiano)
- 🇬🇧 English (Inglese)
- 🇨🇳 Chinese (Cinese)
- 🇯🇵 Japanese (Giapponese)
- 🇰🇷 Korean (Coreano)
- 🇩🇪 German (Tedesco)
- 🇫🇷 French (Francese)
- 🇷🇺 Russian (Russo)
- 🇵🇹 Portuguese (Portoghese)
- 🇪🇸 Spanish (Spagnolo)

**Nota**: Specifica sempre esplicitamente la lingua nella configurazione per migliore qualità.

## Riferimenti

- **Paper**: [Qwen3-TTS Technical Report](https://arxiv.org/abs/2601.15621)
- **Hugging Face**: [Qwen3-TTS Collection](https://huggingface.co/collections/Qwen/qwen3-tts)
- **Blog**: [Qwen AI Blog](https://qwen.ai/blog?id=qwen3tts-0115)
- **Demo Online**: [Qwen3-TTS Space](https://huggingface.co/spaces/Qwen/Qwen3-TTS)

## Licenza

Consulta la licenza del modello Qwen3-TTS su Hugging Face.

## Contributi

Per miglioramenti o bug:
1. Testa con file brevi prima
2. Verifica configurazione in `config/`
3. Controlla log di errore
4. Apri issue con dettagli

## Supporto

Per domande o problemi:
- Consulta [CLAUDE.md](CLAUDE.md) per dettagli tecnici
- Leggi [config/README.md](config/README.md) per configurazioni vocali
- Verifica esempi in questa guida

---

**Sviluppato dal Prof. Sergio Oddi per MacBook Pro M3 Max | Powered by Qwen3-TTS**
