# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Stile di Comunicazione

**IMPORTANTE**:
- Risposte dirette e concise
- NON eseguire comandi automaticamente - aspettare richiesta esplicita dell'utente
- Limitarsi a dare informazioni essenziali, non spiegazioni lunghe

## Progetto Overview

Sistema TTS (Text-to-Speech) locale basato su Qwen3-TTS per generare voci in italiano e inglese su MacBook Pro M3 Max (36GB RAM unificata).

**Obiettivo**: Creare un'architettura user-friendly per la generazione vocale da file di testo con il modello Qwen3-TTS-12Hz-1.7B-VoiceDesign.

## Architettura del Progetto

```
TTS_M3/
├── INPUT/           # File .txt da convertire in audio
├── OUTPUT/          # File audio generati (.wav/.mp3)
├── config/          # File di configurazione per voci e parametri
├── VOICE_SAMPLES/   # Campioni audio per voice cloning
├── app/             # Web app GASSMANN (FastAPI + UI + pipeline) — codice principale
├── tests/           # Suite pytest
├── scripts/         # Script di setup e utilità
├── docs/            # Documentazione completa (questo file)
└── models/          # Cache modelli scaricati (opzionale)
```

## App Standalone GASSMANN

Web app (FastAPI + single-page UI) per clonare voci e generare TTS dal browser.
Nome utente-facing: **GASSMANN** (il sistema TTS sottostante resta Qwen3-TTS).

**Avvio:**
```bash
uvicorn app.main:create_app --factory --host 127.0.0.1 --port 8000   # browser, UI su :8000
./launch.sh                                                          # idem + apre il browser
python -m app.desktop                                               # finestra desktop nativa
# oppure doppio-click su GASSMANN.command (Finder) → app desktop
```

**Struttura:** `app/main.py` (API + serve `app/static/`), `app/pipeline.py`
(generazione + `stitch_scene`), `app/jobs.py` (coda async in-memory), `app/voices.py`
(CRUD voci da `config/*.json`), `app/model_manager.py` (lazy-load modelli),
`app/transcribe.py` (audio→ref_text), `app/desktop.py` (wrapper pywebview),
`app/biochem_text_preprocessor.py` (preprocessing termini scientifici).

**Tab UI:** Genera (singolo) · Batch (più testi, stessa voce) · **Teatro** (voci clone, neutre) · **Teatro-Emozioni** (voci design, Sesso→Voce→Emozione) · Voci.

**Endpoint principali:**
- `GET /api/voices` · `POST /api/voices` (crea clone) · `GET /api/voices/{id}/sample`
- `POST /api/voices/{id}/emotion` (aggiunge variante emotiva: campione + ref_text)
- `POST /api/transcribe`
- `POST /api/generate` → `{job_id}` (campi: text, voice_id, format, biochem, speed, emotion, instruct, temperature, pitch, gain)
- `POST /api/batch` → `{job_id}`
- `POST /api/teatro` → `{job_id}`
- `GET /api/jobs/{jid}` (polling: queued/running/done/error)
- `GET /api/outputs` · `GET /api/outputs/{filename}`

### Funzione TEATRO

Compone una **scena** come sequenza di *speaker block* (battute). Scopo: provare e
imparare le battute di un monologo o dialogo a più voci alternate.

**Campi di ogni speaker block:**
- `character` — etichetta personaggio (solo visuale)
- `voice_id` — voce (dropdown da `/api/voices`); le **varianti emotive** appaiono come
  voci separate (`Sergio · triste`), value `id|emozione` → `emotion` derivata dal menu
- `speed` — velocità: 0.8 / 0.9 / 1.0 / 1.1 / 1.2 (via librosa time-stretch)
- `instruct` — istruzione libera, **solo voci design** (il modello clone la ignora).
  In Teatro-Emozioni: **chip preset** (sussurrato/concitato/…) che si accodano al campo.
- `text` — la battuta
- `pause_after` — secondi di silenzio dopo la battuta nella scena
- **Solo Teatro-Emozioni** — leve extra di resa: `temperature` (espressività, nativa
  modello), `pitch` (semitoni) e `gain` (dB) DSP post via `apply_dsp` in `pipeline.py`
  (euristico, ±2 semitoni ok; per resa "vera" preferire instruct/temperature).
- Azioni per blocco: su / giù / duplica / elimina / **rigenera** (riusa `/api/generate`) ·
  **💾 Salva come voce** (solo Teatro-Emozioni): congela il clip generato come nuova voce
  **clone** riusabile in Teatro. Furbata: `ref_text` = la battuta stessa (no trascrizione);
  riusa `POST /api/voices` + `POST /api/voices/{id}/emotion` (zero backend nuovo).

**IMPORTANTE — emozioni e limite del modello:** il modello Base (voci clonate,
`generate_voice_clone`) **non** supporta `instruct`: l'emozione da testo funziona solo
sul modello VoiceDesign. Su voci clonate l'emozione si ottiene con una **cascata** in
`pipeline.run_generation`:
1. **Campione emotivo** (qualità reale): se la voce ha un `emotion_samples[emotion]`
   nel config, usa quel `ref_audio` (+ relativo `ref_text`) → il clone copia la prosodia.
   Si carica da UI (Voci → "Variante emotiva") o via `POST /api/voices/{id}/emotion`.
2. **DSP fallback** (`apply_emotion_dsp`, euristico): se non c'è campione, applica
   pitch+tempo+gain (`EMOTION_DSP` in `pipeline.py`) — approssima, meno naturale.
- `temperature` → `do_sample`+sampling, alza la vivacità (non direziona l'emozione).
- Per le voci **design** l'emozione passa invece come frase `instruct`
  (`EMOTION_PHRASES` in `pipeline.py`) combinata con `voice_description` + istruzione libera.

Config voce con varianti emotive (esempio):
```json
{ "mode": "voice_clone", "ref_text": "…",
  "emotion_samples": { "felice": "VOICE_SAMPLES/gazzolo_felice.wav" },
  "emotion_ref_texts": { "felice": "trascrizione del campione felice" } }
```

**Output:** `pipeline.stitch_scene` concatena i clip in una traccia unica (con le pause)
+ restituisce i clip singoli. Le scene si esportano/importano come JSON (impostazioni +
testi, no audio) dalla UI.

**Test:** `python -m pytest tests/` (21 test). Singoli runnabili anche come modulo:
`python -m tests.test_stitch` (stitch) · `python -m tests.test_emotion` (DSP).

## Setup Ambiente

### Installazione Dipendenze
```bash
# Creare ambiente virtuale Python 3.12
conda create -n qwen3-tts python=3.12 -y
conda activate qwen3-tts

# Installare qwen-tts package
pip install -U qwen-tts

# Installare soundfile per salvare audio
pip install soundfile

# Per convertire .wav in .mp3 (opzionale)
pip install pydub
# Richiede anche ffmpeg: brew install ffmpeg
```

### Flash Attention 2 (Opzionale ma raccomandato)
```bash
# Su M3 Max con molta RAM, limitare jobs per evitare problemi
MAX_JOBS=4 pip install -U flash-attn --no-build-isolation
```

## Modelli Utilizzati

### Modello Principale: Qwen3-TTS-12Hz-1.7B-VoiceDesign
- **Capacità**: Voice design basato su descrizioni testuali
- **Lingue supportate**: Italiano, Inglese, e altre 8 lingue
- **Streaming**: Sì
- **Controllo tramite istruzioni**: Sì

### Download Modelli (opzionale - auto-download al primo uso)
```bash
# Download manuale se necessario
pip install -U modelscope
modelscope download --model Qwen/Qwen3-TTS-Tokenizer-12Hz --local_dir ./models/Qwen3-TTS-Tokenizer-12Hz
modelscope download --model Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign --local_dir ./models/Qwen3-TTS-12Hz-1.7B-VoiceDesign
```

## Utilizzo del Modello

### Voice Design - Esempio Base
```python
import torch
import soundfile as sf
from qwen_tts import Qwen3TTSModel

model = Qwen3TTSModel.from_pretrained(
    "Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign",
    device_map="mps",  # Usa Metal Performance Shaders su M3 Max
    dtype=torch.bfloat16,
    attn_implementation="flash_attention_2",  # se installato
)

# Generazione singola
wavs, sr = model.generate_voice_design(
    text="Testo da convertire in audio",
    language="Italian",  # o "English", "Chinese", etc.
    instruct="Descrizione della voce desiderata: voce maschile matura, tono caldo e professionale",
)
sf.write("output.wav", wavs[0], sr)
```

### Parametri di Configurazione Vocale

**Formato file di configurazione** (JSON o YAML):
```json
{
  "language": "Italian",
  "voice_description": "Voce femminile giovane, tono amichevole e energico",
  "output_format": "wav",
  "sample_rate": 24000
}
```

**Esempi di descrizioni vocali efficaci**:
- Italiano: "Voce maschile matura, tono professionale e rassicurante, ritmo moderato"
- English: "Young female voice, enthusiastic and friendly tone, clear articulation"

## Comandi Comuni

La vecchia CLI in `src/` è stata rimossa. **Tutto passa dall'app GASSMANN**
(genera singolo, batch, voice cloning, Teatro): vedi sezione "App Standalone GASSMANN".

```bash
uvicorn app.main:create_app --factory --host 127.0.0.1 --port 8000
# oppure ./launch.sh — UI su http://127.0.0.1:8000
```

- **Biochim**: nella tab Genera attiva l'opzione biochem (preprocessing termini
  scientifici via `app/biochem_text_preprocessor.py`). Guida: `docs/BIOCHEMISTRY_TTS_GUIDE.md`.

## Ottimizzazioni per M3 Max

### Utilizzo Memoria
- **RAM Unificata**: 36GB sufficiente per modello 1.7B
- **Device**: Usare `device_map="mps"` per Metal Performance Shaders
- **Dtype**: `torch.bfloat16` per bilanciare qualità e prestazioni

### Parametri di Generazione
- `max_new_tokens=2048`: Default per generazione audio
- Batch processing: Processare 2-4 file contemporaneamente per ottimizzare uso GPU

## Lingue Supportate

Il modello supporta 10 lingue principali:
- Chinese, English, Japanese, Korean
- German, French, Russian, Portuguese, Spanish, Italian

**Nota**: Per migliore qualità, specificare esplicitamente `language` invece di usare "Auto".

## Conversione Formati Audio

### WAV → MP3
```python
from pydub import AudioSegment
audio = AudioSegment.from_wav("output.wav")
audio.export("output.mp3", format="mp3", bitrate="192k")
```

## Note Tecniche

### Tokenizer
- **Qwen3-TTS-Tokenizer-12Hz**: 12.5 fps, 16 codebook, 2048 codebook size
- Compressione acustica efficiente con alta fedeltà
- Preserva informazioni paralinguistiche

### Latenza
- Streaming generation supportato
- Prima generazione: ~1-2 secondi (caricamento modello)
- Generazioni successive: latenza minima in streaming mode

## Voice Cloning

### Modello: Qwen3-TTS-12Hz-1.7B-Base
- **Capacità**: Clonazione vocale da campioni audio (3-10 secondi)
- **Lingue supportate**: Stesso set del VoiceDesign (10 lingue)
- **Cross-lingual**: Sì (voce EN → testo IT mantiene timbro)
- **Streaming**: Sì
- **Requisiti**: Richiede audio di riferimento + trascrizione testuale

### Workflow Voice Cloning

Tutto via app GASSMANN (tab **Voci**): carichi un campione audio (3-10s), l'app
trascrive automaticamente il `ref_text` (`POST /api/transcribe`, mlx-whisper) e crea
la voce clone (`POST /api/voices`). La generazione usa poi quella voce in Genera/Batch/Teatro.
La CLI `src/` (estrazione video, prepare campione, generate/batch) è stata rimossa.

### Configurazione Voice Cloning

**File JSON** (es. `config/gazzolo.json`):
```json
{
  "mode": "voice_clone",
  "language": "Italian",
  "voice_name": "gazzolo",
  "prompt_speech_path": "VOICE_SAMPLES/gazzolo_01.wav",
  "ref_text": "Trascrizione esatta dell'audio di riferimento",
  "output_format": "wav",
  "sample_rate": 24000,
  "voice_notes": "Voce Gazzolo - clonata da campione audio originale"
}
```

**IMPORTANTE**:
- Il campo `ref_text` deve contenere la trascrizione testuale esatta dell'audio di riferimento
- Il campo `voice_name` determina il suffisso del file output: `nome_file_by_{voice_name}.wav`

**Voci disponibili:**
- `gazzolo.json` - Voce Gazzolo naturale
- `gazzolo_docente.json` - Voce Gazzolo con stile docente biochimica
- `capone.json` - Voce Capone naturale
- `capone_docente.json` - Voce Capone con stile docente biochimica

### Best Practices Voice Cloning
- **Durata campione**: 3-10 secondi (ottimale 5-7s)
- **Formato audio**: WAV mono 24kHz
- **Qualità registrazione**: Audio pulito, senza rumori di fondo
- **Contenuto**: Voce naturale, non sussurrata o urlata
- **Cross-lingual**: Funziona ma qualità leggermente inferiore vs. same-language

### Esempio Codice Python
```python
import torch
import soundfile as sf
from qwen_tts import Qwen3TTSModel

model = Qwen3TTSModel.from_pretrained(
    "Qwen/Qwen3-TTS-12Hz-1.7B-Base",
    device_map="mps",
    dtype=torch.bfloat16
)

wavs, sr = model.generate_voice_clone(
    text="Testo da far pronunciare",
    language="Italian",
    ref_audio="VOICE_SAMPLES/speaker.wav",  # 3-10 sec audio
    ref_text="Trascrizione dell'audio di riferimento"  # OBBLIGATORIO
)
sf.write("output.wav", wavs[0], sr)
```

**IMPORTANTE**: Il parametro `ref_text` è obbligatorio e deve contenere la trascrizione esatta dell'audio `ref_audio`.

**Nota**: Vedi `docs/VOICE_CLONING_GUIDE.md` per guida completa.

## TODO / Funzionalità Future

- [ ] Implementare voice mixing (combinare caratteristiche di più voci)
- [ ] Aggiungere voice emotion control (controllo emozioni vocali)
- [ ] Testare voice cloning con diverse lingue source/target
- [ ] **Mode `custom_voice` (Qwen3-TTS-12Hz-1.7B-CustomVoice)**: voce sintetica con
  9 speaker preset + emozione *nativa* via `instruct` (no DSP/cascata). API:
  `model.generate_custom_voice(text, language, speaker, instruct)`. Limiti: voce non
  clonabile (solo preset), nessuno speaker IT nativo (solo EN `Ryan`/`Aiden` cross-lingual).
  Stimato ~30 righe in `pipeline.py` + dropdown speaker nel Teatro. Rimandato: sistema
  attuale funziona, rischio risultato mediocre per l'italiano.
- [ ] **Valutare Chatterbox Multilingual (Resemble AI)** come engine alternativo per
  emozione: 0.5B, 23 lingue (IT incluso), **manopola emozione esplicita** `exaggeration`
  0.25–2.0 (neutro 0.5) — controllo diretto che Qwen3-TTS non ha sui clone. Clone
  zero-shot. Rischi: MPS su Mac segnalato instabile (test "CPU lento / MPS buggy" vs
  Resemble dichiara supporto pieno) → **verificare sul M3**; integrazione = nuovo engine
  (dep `chatterbox` + path in `model_manager.py` + ref format diverso), ~mezza giornata.
  **Mossa prima di integrare**: smoke test standalone (1 battuta IT "arrabbiata") per
  giudicare qualità + velocità. Piano B se MPS scarso: CosyVoice3-MLX (Mac-nativo,
  sub-realtime, emozione a tag, IT incerto). Rif: resemble.ai/chatterbox.

## Guide Pratiche

**Per utenti finali** (⭐ inizia da qui):

- **[TESTO_IN_VOCE.md](TESTO_IN_VOCE.md)** - Guida pratica per convertire testo in audio (2 passi)
- **[CLONAZIONE_VOCE.md](CLONAZIONE_VOCE.md)** - Guida pratica per clonare una voce (3 passi)

**Documentazione dettagliata**:

- **[docs/VOICE_CLONING_GUIDE.md](docs/VOICE_CLONING_GUIDE.md)** - Guida completa voice cloning
- **[docs/BIOCHEMISTRY_TTS_GUIDE.md](docs/BIOCHEMISTRY_TTS_GUIDE.md)** - Guida lezioni scientifiche
- **[docs/VOCI_DISPONIBILI.md](docs/VOCI_DISPONIBILI.md)** - Catalogo voci clonate disponibili
- **[config/README.md](config/README.md)** - Configurazioni voci disponibili

## Riferimenti

- **Paper**: https://arxiv.org/abs/2601.15621
- **Hugging Face**: https://huggingface.co/collections/Qwen/qwen3-tts
- **Blog**: https://qwen.ai/blog?id=qwen3tts-0115
- **Demo Online**: https://huggingface.co/spaces/Qwen/Qwen3-TTS
