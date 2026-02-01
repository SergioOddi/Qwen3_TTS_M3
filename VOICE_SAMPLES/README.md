# VOICE_SAMPLES

Questa cartella contiene i campioni vocali usati per il voice cloning.

## Struttura

```
VOICE_SAMPLES/
├── README.md           # Questo file
├── .gitkeep            # Mantiene cartella in git
├── extracted/          # Audio estratti da video MP4
│   └── .gitkeep
└── [file audio].wav    # I tuoi campioni vocali
```

## Formato Audio Raccomandato

**Ottimale per voice cloning:**
- **Formato**: WAV mono
- **Sample rate**: 24kHz
- **Durata**: 3-10 secondi (ottimale 5-7s)
- **Qualità**: Audio pulito senza rumori di fondo

## Come Aggiungere Campioni

### Metodo 1: Estrai da Video MP4

```bash
# Estrai 5 secondi dal secondo 10
python src/extract_audio_from_video.py -i video.mp4 -o VOICE_SAMPLES/speaker.wav --start 10 --duration 5
```

### Metodo 2: Copia File Audio Esistente

```bash
# Copia file WAV/MP3
cp ~/Downloads/audio.wav VOICE_SAMPLES/

# Ottimizza (opzionale)
python src/prepare_voice_sample.py -i VOICE_SAMPLES/audio.wav -o VOICE_SAMPLES/audio_clean.wav
```

### Metodo 3: Prepara da Audio Lungo

```bash
# Suggerisci miglior segmento
python src/prepare_voice_sample.py -i audio_lungo.mp3 --suggest

# Estrai e ottimizza
python src/prepare_voice_sample.py -i audio_lungo.mp3 -o VOICE_SAMPLES/voice.wav --start 10 --duration 5
```

## Lista Campioni Disponibili

```bash
python src/list_voice_samples.py
```

## Best Practices

✓ **Usa audio di alta qualità:**
- Registrazioni pulite
- Voce naturale
- Senza rumori di fondo

✓ **Durata ottimale:**
- 5-7 secondi è ideale
- Minimo 3 secondi
- Massimo 10 secondi

✓ **Formato:**
- WAV mono 24kHz preferito
- MP3 >= 128kbps accettabile

✗ **Evita:**
- Audio con musica di sottofondo
- Voci sussurrate o urlate
- Registrazioni con eco/riverbero
- File troppo corti (< 3s)

## Convenzioni di Naming

**Formato raccomandato**: `nome_descrittivo_NN.wav`

```
VOICE_SAMPLES/
├── gazzolo_01.wav           # Voce professore - campione 1
├── narratore_uomo_01.wav    # Voce maschile narrazione
├── professore_02.wav        # Altro professore - campione 2
└── extracted/               # Audio estratti da video
    ├── intervista_2024.wav
    └── podcast_episode.wav
```

**Note**:
- Usa nomi descrittivi e chiari
- Aggiungi `_NN` per campioni multipli dello stesso speaker
- Per ogni campione crea corrispondente config in `config/clone_nome.json`

## Note

- I file in questa cartella sono ignorati da git (vedi `.gitignore`)
- I campioni vocali non vengono inclusi nel repository
- Ogni utente deve creare i propri campioni localmente

## Lista Voci Clonate Disponibili

Per vedere tutte le voci disponibili con caratteristiche e istruzioni d'uso:

👉 **[docs/VOCI_DISPONIBILI.md](../docs/VOCI_DISPONIBILI.md)**

## Risorse

- **Voci disponibili**: `docs/VOCI_DISPONIBILI.md` ⭐
- **Guida completa**: `docs/VOICE_CLONING_GUIDE.md`
- **Esempi**: `EXAMPLES.md`
- **Documentazione**: `CLAUDE.md`
