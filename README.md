# TTS_M3 - Converti Testo in Audio

Sistema Text-to-Speech locale che converte file di testo in audio naturale. Basato su Qwen3-TTS, funziona al 100% offline su MacBook Pro M3 Max.

---

## 🚀 App standalone (web UI locale)

Avvia l'interfaccia grafica nel browser:

```bash
./launch.sh
```

Si apre su http://127.0.0.1:8000 con tre schede:
- **Genera** — testo → voce → audio (player + download wav/mp3)
- **Batch** — più testi in coda con la stessa voce
- **Voci** — libreria voci con preview + creazione voce clonata (registra dal
  microfono o carica un file, trascrizione automatica Whisper o manuale)

Tutto in locale e offline. Prima generazione più lenta (caricamento modello).

---

## 🚀 Guide Pratiche

📝 **[TESTO_IN_VOCE.md](TESTO_IN_VOCE.md)** - Converti testo in audio (2 passi)
🎙️ **[CLONAZIONE_VOCE.md](CLONAZIONE_VOCE.md)** - Clona una voce reale (3 passi)

---

## ⚡ Esempi Rapidi

Tutto passa dall'app GASSMANN (`./launch.sh`, tab **Genera**): scrivi/incolla il
testo, scegli la voce dal menu (incluse le voci clonate come Sermonti, Gazzolo,
Capone) e genera. Vedi [TESTO_IN_VOCE.md](TESTO_IN_VOCE.md) per la guida passo passo.






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

1. Apri l'app (`./launch.sh`), tab **Genera**
2. Scrivi/incolla il testo, scegli voce e formato (wav/mp3)
3. Genera → scarica il file da **Output** o dalla lista risultati

**È così semplice!**

---

## 🎯 Elaborazione Batch

Tab **Batch** dell'app: incolla più testi (uno per riga o blocco), scegli una
voce comune, genera tutti in coda.

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

Tab **Genera** → incolla "La biochimica è lo studio delle reazioni chimiche
negli organismi viventi." → scegli una voce italiana → Genera.

### Esempio 2: Cambiare Voce

Stesso testo, cambia solo la voce dal menu a tendina (femminile, clonata
Gazzolo, inglese per testo EN, ecc.) — nessun comando da riscrivere.

### Esempio 3: Lezioni di Biochimica

Tab **Genera**, opzione **Biochim** attiva: corregge automaticamente la
pronuncia di termini come "ATP", "NADH", "enzima", ecc. (vedi
[docs/BIOCHEMISTRY_TTS_GUIDE.md](docs/BIOCHEMISTRY_TTS_GUIDE.md)).

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

Poi selezionala dal menu voci nell'app (compare in automatico leggendo `config/`).

### Voice Cloning (clona una voce reale)

Tab **Voci** dell'app: registra dal microfono o carica un file (5-10s),
trascrizione automatica o manuale del `ref_text`, salva → la voce è pronta
in Genera/Batch/Teatro. Vedi [CLONAZIONE_VOCE.md](CLONAZIONE_VOCE.md).

---

## 📁 Struttura Progetto

```
TTS_M3/
├── INPUT/              # Metti qui i file .txt da convertire
├── OUTPUT/             # Trovi qui gli audio generati (.wav/.mp3)
├── config/             # Configurazioni voci (personalizza qui)
├── VOICE_SAMPLES/      # Campioni audio per voice cloning
├── app/                # Web app GASSMANN (FastAPI + UI + pipeline)
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

Se hai problemi con GPU, modifica `app/model_manager.py` e cambia `device_map="mps"` in `device_map="cpu"`.

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
