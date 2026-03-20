# 📝 Testo in Voce - Guida Pratica

Questa guida ti spiega come convertire un testo in audio in modo semplice e veloce.

## Lettura testo inglese da SPEAKER INGLESE_002b
#per un buon tts di testo da slide di una lezione un ottimo modello è questo: 
python src/batch_clone_process.py -c config/INGLESE_002i.json





---

## ⚡ Quick Start (2 passi)

### 1️⃣ Crea un File di Testo

```bash
echo "Benvenuto al sistema di sintesi vocale. Questo è un test." > INPUT/mio_testo.txt
```

O copia un file esistente:
```bash
cp ~/Documents/testo.txt INPUT/
```

### 2️⃣ Genera l'Audio

```bash
python src/generate_audio.py -i INPUT/mio_testo.txt
```

**Output**: `OUTPUT/mio_testo.wav`

**È così semplice!** 🎉

---

## 🎤 Cambiare Voce

Usa `-c config/voce.json` per personalizzare la voce.

### Voci Maschili Italiane

```bash
# Voce professionale (default)
python src/generate_audio.py -i INPUT/testo.txt -c config/voice_config.json

# Voce narratore
python src/generate_audio.py -i INPUT/testo.txt -c config/voice_config_narratore.json

# Voce documentaristica
python src/generate_audio.py -i INPUT/testo.txt -c config/voice_config_narratore_documentaristico.json
```

### Voci Femminili Italiane

```bash
# Voce femminile professionale
python src/generate_audio.py -i INPUT/testo.txt -c config/voice_config_female.json

# Voce giovane ed energica
python src/generate_audio.py -i INPUT/testo.txt -c config/voice_config_narratrice_giovane.json

# Voce matura ed elegante
python src/generate_audio.py -i INPUT/testo.txt -c config/voice_config_narratrice_elegante.json
```

### Voci Inglesi

```bash
# Voce maschile professionale
python src/generate_audio.py -i INPUT/english_text.txt -c config/voice_config_english.json

# Voce documentaristica BBC-style
python src/generate_audio.py -i INPUT/english_text.txt -c config/voice_config_narrator_documentary_en.json
```

---

## 📚 Elaborazione Batch

Converti tutti i file `.txt` nella cartella INPUT in un colpo solo.

```bash
# Usa voce default
python src/batch_process.py

# Con voce specifica
python src/batch_process.py -c config/voice_config_female.json
```

**Nota**: Il modello viene caricato una sola volta, rendendo il batch molto veloce.

---

## 🎯 Esempi Pratici

### Esempio 1: Audiolibro Semplice

```bash
# 1. Crea il testo
cat > INPUT/storia.txt << 'EOF'
C'era una volta, in un piccolo villaggio di montagna,
un vecchio saggio che conosceva i segreti della natura.
Ogni giorno, al tramonto, raccontava storie ai bambini del paese.
EOF

# 2. Genera audio con voce narratore
python src/generate_audio.py -i INPUT/storia.txt -c config/voice_config_narratore.json

# Output: OUTPUT/storia.wav
```

### Esempio 2: Lezione Scientifica

```bash
# 1. Crea testo lezione
echo "La biochimica studia le reazioni chimiche negli organismi viventi.
Gli enzimi sono catalizzatori biologici che accelerano le reazioni metaboliche." > INPUT/lezione_biochimica.txt

# 2. Genera con preprocessor scientifico
python src/generate_biochem_lecture.py -i INPUT/lezione_biochimica.txt

# Output: OUTPUT/lezione_biochimica.wav
```

Il preprocessor corregge automaticamente la pronuncia di termini scientifici (ATP, DNA, enzimi, ecc.).

### Esempio 3: Contenuto Multi-Lingua

```bash
# Testo italiano
echo "Ciao, benvenuto!" > INPUT/italiano.txt
python src/generate_audio.py -i INPUT/italiano.txt -c config/voice_config.json

# Testo inglese
echo "Hello, welcome!" > INPUT/english.txt
python src/generate_audio.py -i INPUT/english.txt -c config/voice_config_english.json

# Testo spagnolo
echo "Hola, bienvenido!" > INPUT/spanish.txt
python src/generate_audio.py -i INPUT/spanish.txt -c config/voice_config_spanish.json
```

---

## 🔧 Personalizza la Voce

### Crea una Nuova Configurazione

Crea un file JSON in `config/mia_voce_custom.json`:

```json
{
  "language": "Italian",
  "voice_description": "Voce maschile giovane, tono amichevole ed energico, ritmo veloce",
  "output_format": "wav",
  "sample_rate": 24000
}
```

Poi usalo:
```bash
python src/generate_audio.py -i INPUT/testo.txt -c config/mia_voce_custom.json
```

### Esempi di Voice Description

**Voce Calda e Rassicurante:**
```json
"voice_description": "Voce maschile matura, tono caldo e rassicurante, ritmo calmo e rilassato, articolazione chiara"
```

**Voce Energica e Dinamica:**
```json
"voice_description": "Voce femminile giovane, tono vivace ed energico, ritmo veloce, articolazione precisa"
```

**Voce Professionale Documentaristica:**
```json
"voice_description": "Voce maschile profonda e autorevole, tono equilibrato, dizione impeccabile, stile documentaristico"
```

**Voce Intima e Riflessiva:**
```json
"voice_description": "Voce maschile baritonale, tono confidenziale e riflessivo, parlata pacata, timbro caldo"
```

---

## 🌍 Lingue Supportate

Il sistema supporta 10 lingue:

| Lingua | Codice | Esempio Configurazione |
|--------|--------|------------------------|
| 🇮🇹 Italiano | `Italian` | `config/voice_config.json` |
| 🇬🇧 Inglese | `English` | `config/voice_config_english.json` |
| 🇪🇸 Spagnolo | `Spanish` | `config/voice_config_spanish.json` |
| 🇫🇷 Francese | `French` | - |
| 🇩🇪 Tedesco | `German` | - |
| 🇵🇹 Portoghese | `Portuguese` | - |
| 🇷🇺 Russo | `Russian` | - |
| 🇨🇳 Cinese | `Chinese` | - |
| 🇯🇵 Giapponese | `Japanese` | - |
| 🇰🇷 Coreano | `Korean` | - |

**Nota**: Specifica sempre la lingua nel file di configurazione per miglior qualità.

---

## 📁 Organizzazione File

### Struttura Consigliata

```
TTS_M3/
├── INPUT/                  # I tuoi file di testo (.txt)
│   ├── capitolo1.txt
│   ├── capitolo2.txt
│   └── lezione_biochimica.txt
│
├── OUTPUT/                 # Audio generati (.wav)
│   ├── capitolo1.wav
│   ├── capitolo2.wav
│   └── lezione_biochimica.wav
│
└── config/                 # Configurazioni voci
    ├── voice_config.json
    └── mia_voce_custom.json
```

### Workflow Tipo

```bash
# 1. Metti testi in INPUT/
cp ~/Documents/*.txt INPUT/

# 2. Scegli voce (o usa default)
# 3. Genera tutto in batch
python src/batch_process.py -c config/voice_config_narratore.json

# 4. Trova audio in OUTPUT/
ls -la OUTPUT/
```

---

## ⚡ Performance

Su **MacBook Pro M3 Max (36GB RAM)**:

- **Prima generazione**: ~1-2 secondi (caricamento modello)
- **Generazioni successive**: Quasi istantanee in streaming
- **Batch processing**: Molto veloce (modello caricato una volta)
- **Uso RAM**: ~5-8GB
- **100% offline**: Funziona senza internet

---

## 🎓 Casi d'Uso Speciali

### Lezioni Scientifiche/Biochimica

```bash
# Usa il preprocessor per termini scientifici
python src/generate_biochem_lecture.py -i INPUT/lezione.txt -c config/voice_config.json

# Preview del preprocessing senza generare audio
python src/generate_biochem_lecture.py -i INPUT/lezione.txt -o dummy.wav --preview-preprocessing
```

**Termini corretti automaticamente:**
- ATP → "A-T-P"
- DNA → "D-N-A"
- NADH → "N-A-D-H"
- pH → "pi-acca"
- Enzima, proteina, glucosio (pronuncia corretta)

Vedi [docs/BIOCHEMISTRY_TTS_GUIDE.md](docs/BIOCHEMISTRY_TTS_GUIDE.md) per la guida completa.

---

## 🔄 Convertire WAV in MP3

```bash
# Installa ffmpeg (se non già installato)
brew install ffmpeg

# Converti manualmente
ffmpeg -i OUTPUT/audio.wav -b:a 192k OUTPUT/audio.mp3
```

O usa pydub in Python:
```python
from pydub import AudioSegment
audio = AudioSegment.from_wav("OUTPUT/audio.wav")
audio.export("OUTPUT/audio.mp3", format="mp3", bitrate="192k")
```

---

## ❓ Problemi Comuni

### Il modello non si scarica

```bash
# Download manuale
pip install -U modelscope
modelscope download --model Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign --local_dir ./models/Qwen3-TTS-12Hz-1.7B-VoiceDesign
```

### Errore "device_map"

Se hai problemi con GPU, modifica `src/generate_audio.py`:
```python
device_map="cpu"  # invece di "mps"
```

### Conversione MP3 fallisce

```bash
# Installa ffmpeg
brew install ffmpeg
```

### Voce non naturale

- Prova configurazioni diverse
- Aumenta dettagli in `voice_description`
- Usa preprocessing per termini tecnici

---

## 🎨 Configurazioni Voci Disponibili

### Voice Design (Descrizione Testuale)

| File | Lingua | Tipo | Descrizione |
|------|--------|------|-------------|
| `voice_config.json` | IT | Maschile | Professionale generale |
| `voice_config_female.json` | IT | Femminile | Energica e amichevole |
| `voice_config_narratore.json` | IT | Maschile | Narratore professionale |
| `voice_config_narratore_documentaristico.json` | IT | Maschile | Stile documentario |
| `voice_config_narratrice_giovane.json` | IT | Femminile | Giovane ed energica |
| `voice_config_narratrice_elegante.json` | IT | Femminile | Matura ed elegante |
| `voice_config_english.json` | EN | Maschile | Professionale inglese |
| `voice_config_narrator_documentary_en.json` | EN | Maschile | BBC-style |

Vedi [config/README.md](config/README.md) per lista completa e dettagli.

### Voice Cloning (Voci Clonate)

Se vuoi usare voci clonate da campioni audio reali, vedi [CLONAZIONE_VOCE.md](CLONAZIONE_VOCE.md).

---

## 📖 Documentazione Avanzata

- [CLONAZIONE_VOCE.md](CLONAZIONE_VOCE.md) - Clona voci reali
- [docs/QUICKSTART.md](docs/QUICKSTART.md) - Guida rapida
- [docs/EXAMPLES.md](docs/EXAMPLES.md) - Esempi avanzati
- [docs/BIOCHEMISTRY_TTS_GUIDE.md](docs/BIOCHEMISTRY_TTS_GUIDE.md) - Lezioni scientifiche
- [config/README.md](config/README.md) - Dettagli configurazioni
- [CLAUDE.md](CLAUDE.md) - Documentazione tecnica completa

---

**Sviluppato per MacBook Pro M3 Max | Powered by Qwen3-TTS**
