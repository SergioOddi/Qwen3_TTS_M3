# 🎙️ Clonazione Voce - Guida Pratica

Questa guida ti spiega come clonare una voce in 3 semplici passi, dalla tab
**Voci** dell'app GASSMANN.

---

## ⚡ Quick Start (3 passi)

### 1️⃣ Prepara un Campione Audio (5-7 secondi)

Un file audio pulito (WAV/MP3/altro formato comune) con voce naturale, non
sussurrata né urlata. Puoi registrarlo al momento dal microfono nella tab
Voci, oppure caricare un file esistente.

### 2️⃣ Trascrivi l'Audio

Nella tab Voci, dopo aver caricato/registrato il campione:

- **Trascrizione manuale**: ascolta e scrivi esattamente cosa viene detto
  (il `ref_text` deve corrispondere parola per parola all'audio)

Esempio:
- Audio dice: *"Buongiorno, oggi parliamo di biochimica"*
- Trascrizione: `Buongiorno, oggi parliamo di biochimica`

### 3️⃣ Salva la Voce

Dai un nome alla voce e salva. L'app crea in automatico il file
`config/<nome>.json` e il campione in `VOICE_SAMPLES/<nome>.wav`:

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

La voce è ora selezionabile in **Genera**, **Batch** e **Teatro**.

**Nota**: creare una voce con un nome già esistente viene bloccato dall'app
(errore "voce già esiste") — non sovrascrive mai una voce esistente in silenzio.

---

## 🚀 Utilizzo

Seleziona la voce clonata dal menu voci in **Genera** o **Batch** esattamente
come una voce design — nessun comando, nessun file da editare a mano.

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

Il progetto include già alcune voci pronte all'uso (selezionabili dal menu):

| Voce | Ideale per |
|------|------------|
| Gazzolo | Narrazione naturale |
| Gazzolo Docente | Lezioni biochimica |
| Capone | Narrazione generale |
| Capone Docente | Contenuti didattici |
| Sermonti | Narrazione classica |
| Sermonti Narratore | Storytelling |

Catalogo completo in [docs/VOCI_DISPONIBILI.md](docs/VOCI_DISPONIBILI.md).

---

## 🎭 Varianti Emotive

Una voce clonata può avere **campioni emotivi** aggiuntivi (es. `Gazzolo_felice`):
si aggiungono dalla tab Voci ("Variante emotiva") caricando un secondo campione
con la relativa trascrizione. Compaiono come voci separate nella palette del
Teatro. Dettagli in [CLAUDE.md](CLAUDE.md#funzione-teatro).

---

## 🌍 Clonazione Multi-Lingua

Puoi clonare una voce in una lingua e farla parlare in un'altra: nella tab
Voci imposta `language` sulla lingua del **testo di destinazione** (non
dell'audio campione). La qualità è leggermente inferiore rispetto a
same-language cloning.

---

## ❓ Problemi Comuni

### Voce non trovata / campione mancante

Controlla in `config/<nome>.json` che `prompt_speech_path` punti a un file
esistente in `VOICE_SAMPLES/`.

### Qualità scadente

- Verifica durata campione (5-7 secondi ottimale)
- Usa audio pulito senza rumori
- Evita campioni troppo corti (< 3s)

### Voce robotica

- Migliora qualità campione source
- Usa campione più lungo (6-7 secondi)
- Verifica che la trascrizione `ref_text` sia esatta parola per parola

---

## 📚 Documentazione Completa

- [docs/VOICE_CLONING_GUIDE.md](docs/VOICE_CLONING_GUIDE.md) - Guida dettagliata
- [docs/VOCI_DISPONIBILI.md](docs/VOCI_DISPONIBILI.md) - Catalogo voci
- [CLAUDE.md](CLAUDE.md) - Documentazione tecnica

---

**Sviluppato per MacBook Pro M3 Max | Powered by Qwen3-TTS**
