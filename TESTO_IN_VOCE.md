# 📝 Testo in Voce - Guida Pratica

Questa guida ti spiega come convertire un testo in audio usando l'app GASSMANN.

---

## ⚡ Quick Start (2 passi)

### 1️⃣ Avvia l'app

```bash
./launch.sh
```

Si apre su `http://127.0.0.1:8000`.

### 2️⃣ Genera l'audio

Tab **Genera** → incolla o scrivi il testo → scegli voce e formato (wav/mp3) → **Genera**.

**Output**: scaricabile dal player o dalla cartella `OUTPUT/`.

**È così semplice!** 🎉

---

## 🎤 Cambiare Voce

Il menu voci nella tab Genera elenca sia le voci **Voice Design** (descrizione
testuale) sia le voci **clonate** (vedi [CLONAZIONE_VOCE.md](CLONAZIONE_VOCE.md)).
Cambiarla è un click sul menu a tendina — nessun file da modificare.

---

## 📚 Elaborazione Batch

Tab **Batch**: incolla più testi (uno per blocco), scegli una voce comune,
genera tutti in coda. Il modello resta caricato in memoria, quindi il batch è
molto più rapido della prima generazione.

---

## 🎭 Teatro (dialoghi multi-voce)

Per monologhi o scene con più personaggi/voci alternate, usa la tab **Teatro**
(voci clonate) o **Teatro-Emozioni** (voci design con controllo emozione).
Dettagli completi nel [CLAUDE.md](CLAUDE.md#funzione-teatro).

---

## 🔧 Personalizza una Voce Design

Le voci Voice Design sono descritte a testo. Per crearne una nuova, aggiungi
un file in `config/mia_voce_custom.json`:

```json
{
  "language": "Italian",
  "voice_description": "Voce maschile giovane, tono amichevole ed energico, ritmo veloce",
  "output_format": "wav",
  "sample_rate": 24000
}
```

Ricaricando l'app la voce compare da sola nel menu (letta da `config/`).

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

| Lingua | Codice |
|--------|--------|
| 🇮🇹 Italiano | `Italian` |
| 🇬🇧 Inglese | `English` |
| 🇪🇸 Spagnolo | `Spanish` |
| 🇫🇷 Francese | `French` |
| 🇩🇪 Tedesco | `German` |
| 🇵🇹 Portoghese | `Portuguese` |
| 🇷🇺 Russo | `Russian` |
| 🇨🇳 Cinese | `Chinese` |
| 🇯🇵 Giapponese | `Japanese` |
| 🇰🇷 Coreano | `Korean` |

**Nota**: specifica sempre la lingua per la miglior qualità.

---

## 🎓 Lezioni Scientifiche/Biochimica

Nella tab Genera attiva l'opzione **Biochim**: corregge automaticamente la
pronuncia di termini come:

- ATP → "A-T-P"
- DNA → "D-N-A"
- NADH → "N-A-D-H"
- pH → "pi-acca"
- enzima, proteina, glucosio (pronuncia corretta)

Vedi [docs/BIOCHEMISTRY_TTS_GUIDE.md](docs/BIOCHEMISTRY_TTS_GUIDE.md) per la guida completa.

---

## ❓ Problemi Comuni

### Il modello non si scarica

```bash
pip install -U modelscope
modelscope download --model Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign --local_dir ./models/Qwen3-TTS-12Hz-1.7B-VoiceDesign
```

### Errore GPU / "device_map"

Se hai problemi con MPS, modifica `app/model_manager.py` e cambia
`device_map="mps"` in `device_map="cpu"`.

### Conversione MP3 fallisce

```bash
brew install ffmpeg
```

### Voce non naturale

- Prova un'altra voce dal menu
- Aumenta dettagli in `voice_description` (per le voci design)
- Attiva Biochim per testi tecnici

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
