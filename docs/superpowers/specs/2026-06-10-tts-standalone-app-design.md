# TTS_M3 — App Standalone (Web App Locale)

**Data**: 2026-06-10
**Stato**: Design approvato, in attesa di review spec

## Obiettivo

Trasformare il progetto TTS_M3 (oggi una collezione di script CLI Python attorno a
Qwen3-TTS) in un'app standalone moderna, locale e offline, che permetta di:

1. Generare audio da testo usando le voci disponibili (voice design + voci clonate).
2. Clonare voci reali da un campione audio e riutilizzarle per il TTS.
3. Gestire un set di voci e testi facili da compilare e usare, tramite UI.

Tutto gira in locale sul MacBook Pro M3 Max: nessun servizio esterno, nessuna
connessione richiesta a runtime.

## Contesto esistente (da riusare, non riscrivere)

- **Modelli** (già scaricati in `~/.cache/huggingface/hub`):
  - `Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign` → generazione da descrizione voce.
  - `Qwen/Qwen3-TTS-12Hz-1.7B-Base` → voice cloning (richiede `ref_audio` + `ref_text`).
- **Ambiente**: `.venv` Python 3.12 con `qwen-tts 0.0.5`, `torch 2.10`, `fastapi`,
  `uvicorn`, `librosa`, `pydub`, `soundfile` già installati.
- **Codice riusabile**:
  - `src/generate_audio.py` → core voice design (`model.generate_voice_design`).
  - `src/generate_cloned_audio.py` → core voice cloning (`model.generate_voice_clone`),
    incl. `instruct`, `speed_factor` (time-stretch librosa), conversione mp3.
  - `src/biochem_text_preprocessor.py` → preprocessing terminologia scientifica.
  - `src/audio_converter.py` → conversione wav→mp3 (pydub).
- **Config voci**: `config/*.json` nel formato esistente. Due tipi:
  - *Voice design*: `{ language, voice_description, output_format }`.
  - *Voice clone*: `{ mode:"voice_clone", language, voice_name, prompt_speech_path,
    ref_text, instruct?, speed_factor?, output_format, voice_notes? }`.
- **Cartelle**: `INPUT/` (testi), `OUTPUT/` (audio generati), `VOICE_SAMPLES/`
  (campioni per cloning).

### Dipendenze nuove
- `mlx-whisper` — trascrizione automatica del campione audio (`ref_text`), ottimizzato
  Metal su M3. Aggiunta a `requirements.txt`. Caricamento lazy: solo se l'utente usa la
  trascrizione auto.

## Approccio scelto

**FastAPI + UI vanilla offline.** Backend FastAPI (già installato) che espone una REST
API e serve una single-page app scritta a mano in HTML/CSS/JS senza CDN né build step,
così l'app resta 100% offline e senza toolchain Node. Scartati: Gradio (look generico,
poco controllo), React/Vite (build + Node, eccessivo per uso locale singolo).

## Architettura

Nuova cartella `app/`, isolata. Il codice in `src/` non viene modificato; le funzioni
core vengono importate/riusate.

```
app/
  main.py            # FastAPI: definizione route REST + mount static UI
  model_manager.py   # singleton lazy-load dei 2 modelli TTS, funzioni generate
  jobs.py            # coda job in-process (1 worker) + tracking stato/progress
  voices.py          # lettura/scrittura config/*.json + VOICE_SAMPLES/
  transcribe.py      # wrapper mlx-whisper per ref_text automatico
  static/
    index.html
    app.js
    style.css
launch.sh            # avvia uvicorn e apre il browser su localhost
```

### Componenti

**`model_manager.py`** — Carica i modelli alla prima richiesta che ne ha bisogno e li
tiene residenti in RAM (1.7B bf16 ≈ 3.5 GB ciascuno; 36 GB disponibili). Tenta
`flash_attention_2`, fallback a implementazione standard, device `mps`. Espone:
- `generate_design(text, language, voice_description) -> (wav, sr)`
- `generate_clone(text, language, ref_audio, ref_text, instruct?, speed_factor?) -> (wav, sr)`
- `status()` → quali modelli sono caricati.
Interfaccia: input puri (testo + parametri), output array audio + sample rate. Nessuna
dipendenza dal layer HTTP.

**`jobs.py`** — Generazione = job asincrono (secondi/minuti). Coda in-process con **un
solo worker** (il modello non è concorrente). Ogni job ha: id, tipo (single/batch),
stato (queued/running/done/error), progress (0..1, per batch = item fatti/totali),
risultato (path file output) o messaggio d'errore. Niente DB: stato in memoria +
file su disco in `OUTPUT/`.

**`voices.py`** — CRUD sul formato config esistente. Funzioni:
- `list_voices()` → elenco normalizzato: id (nome file senza estensione), tipo
  (design|clone), language, descrizione/note, tag, path campione (se clone).
- `get_sample_path(id)` → per la preview audio.
- `create_clone(name, language, audio_bytes, ref_text, instruct?, tags?)` → converte il
  campione in WAV mono 24 kHz, lo salva in `VOICE_SAMPLES/`, scrive `config/<name>.json`,
  ritorna la voce creata. Accetta sia upload di file sia blob registrato dal microfono.
Tag derivati da convenzioni esistenti (es. suffisso `_docente`, `_narratore`) e/o campo
`tags` aggiunto al JSON.

**`transcribe.py`** — `transcribe(audio_path, language) -> str`. Carica mlx-whisper in
modo lazy. Usato solo dall'endpoint di trascrizione.

**`main.py`** — Route (prefisso `/api`):
- `GET  /api/voices` → lista voci con metadati e tag.
- `GET  /api/voices/{id}/sample` → stream audio campione per preview.
- `POST /api/voices` → crea voce clonata (multipart: audio, name, language, ref_text,
  instruct?, tags?).
- `POST /api/transcribe` → multipart audio → `{ text }` (Whisper auto).
- `POST /api/generate` → `{ text, voice_id, biochem?, speed?, format }` → `{ job_id }`.
- `POST /api/batch` → `{ items:[{name,text}], voice_id, biochem?, format }` → `{ job_id }`.
- `GET  /api/jobs/{id}` → stato/progress/risultato.
- `GET  /api/outputs` → elenco file generati; `GET /api/outputs/{file}` → download.
- `GET  /` + `/static/*` → la UI.

### Flusso dati

1. UI → `POST /api/generate` con testo + voce scelta → riceve `job_id`.
2. `jobs.py` accoda; il worker chiama `voices.py` per risolvere la voce in parametri,
   applica preprocessing biochimica se richiesto, chiama `model_manager` (design o
   clone), salva in `OUTPUT/` (wav, e mp3 se richiesto via converter esistente).
3. UI fa polling `GET /api/jobs/{id}` finché `done` → mostra player + link download.
4. Batch: stesso flusso, il worker itera gli item aggiornando il progress.

### UI (3 schede)

1. **Genera** — textarea testo, select voce (con preview), toggle preprocessing
   biochimica, slider velocità, scelta formato wav/mp3, bottone genera → barra
   progresso → player HTML5 + download.
2. **Batch** — aggiunta di più testi (incolla o carica .txt), una voce comune, avvio
   coda, lista risultati con stato e download per ciascuno.
3. **Voci** — catalogo voci con tag e preview audio; form "Nuova voce clonata":
   sorgente campione = **registrazione dal microfono del Mac** (MediaRecorder API del
   browser, offline, niente dipendenze extra) **oppure** upload di un file audio → si
   riascolta il campione → bottone "Trascrivi" (Whisper) **oppure** ref_text manuale →
   nome, lingua, instruct opzionale, tag → salva.

### Registrazione microfono

- Cattura via `navigator.mediaDevices.getUserMedia` + `MediaRecorder` nel browser:
  pulsante rec/stop, timer, waveform o livello opzionale, riascolto prima di salvare.
- Il blob registrato (webm/ogg) viene inviato a `POST /api/voices` come fa l'upload.
  Lato server, `voices.py` converte il campione in WAV mono 24 kHz (formato atteso dal
  cloning) con pydub/soundfile prima di salvarlo in `VOICE_SAMPLES/`.
- Stesso blob riusabile per `POST /api/transcribe` (trascrizione auto del ref_text).
- Richiede contesto sicuro: `127.0.0.1`/`localhost` è considerato sicuro dai browser,
  quindi getUserMedia funziona senza HTTPS.

### Gestione errori

- Modello che non carica → job in stato `error` con messaggio leggibile; la UI lo mostra
  senza crashare.
- Campione audio mancante / `ref_text` vuoto per un clone → validazione lato API con
  errore 400 chiaro.
- Whisper non installato → endpoint transcribe risponde con messaggio che invita alla
  trascrizione manuale (la creazione voce resta possibile a mano).
- File input vuoto / testo vuoto → 400.

### Avvio

`launch.sh`: attiva `.venv`, lancia `uvicorn app.main:app --host 127.0.0.1 --port 8000`,
poi `open http://127.0.0.1:8000`. Documentato nel README.

## Testing

- **Unit** (senza caricare i modelli): `voices.py` (parse/normalizzazione config esistenti,
  create_clone scrive JSON corretto), `jobs.py` (transizioni di stato, progress batch).
- **Integrazione leggera**: endpoint API con `model_manager` mockato (no GPU): verifica
  routing, validazioni, polling job, lista/download output.
- **Smoke manuale**: una generazione design reale e una clone reale (es. voce `zaza02`)
  per confermare che la pipeline col modello vero funziona end-to-end.
- Mock del modello per evitare caricamenti pesanti nei test automatici.

## Fuori scope (prima versione)

- Streaming audio in tempo reale durante la generazione.
- Multi-utente / autenticazione (app locale single-user).
- Voice mixing ed emotion control avanzati (già TODO futuri nel progetto).
- Packaging in `.app`/`.dmg` (resta web app locale; eventuale step successivo).
```
