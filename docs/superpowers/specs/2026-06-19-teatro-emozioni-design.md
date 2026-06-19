# Tab Teatro-Emozioni — Design

Data: 2026-06-19 · Branch: `SINTETIZZA_VOCI`

## Obiettivo

Separare nell'UI le voci **clonate** (timbri reali) dalle voci **design**
(sintetiche, con emozione nativa via `instruct`):

- **Teatro** (esistente): solo voci clone, neutre. Niente voci design, niente
  varianti emotive nel menu.
- **Teatro-Emozioni** (nuovo): solo voci design. Per ogni battuta si sceglie
  **Sesso → Voce → Emozione**.

Motivazione: le voci design rendono l'emozione meglio dei cloni (instruct nativo
vs DSP/cascata). Tenere i due flussi separati evita confusione e menu sovraccarichi.

## Stato di partenza (branch SINTETIZZA_VOCI, non committato)

- `voices.py`: aggiunto `SELECTABLE_EMOTIONS`; le voci design espongono tutte le
  emozioni come `emotions` (emozione nativa via instruct).
- `config/attore.json` (M) e `config/attrice.json` (F): voci design IT per teatro.
  Il sesso è solo nella `voice_description`, **non** in un campo dedicato.
- `tests/test_voices.py`: aggiornato per il nuovo `emotions` delle voci design.

Il design qui sotto si appoggia a questo stato (nessun conflitto).

## Backend

### 1. Campo `gender` nelle voci design
- `config/attore.json` → `"gender": "male"`
- `config/attrice.json` → `"gender": "female"`

### 2. Esporre `gender` in `voices.py`
In `_voice_info` aggiungere al dict ritornato:
```python
"gender": data.get("gender"),   # "male" | "female" | None (cloni)
```
Serve al frontend per filtrare le voci design per sesso.

### 3. Test
In `tests/test_voices.py`: assert che una voce design con `gender` lo espone in
`list_voices()`; che una voce senza campo dà `gender == None`.

## Frontend

### 4. index.html
- **Nav**: nuovo pulsante `<button class="tab" data-tab="teatro-emo">Teatro-Emozioni</button>`.
- **Sezione** `<section id="teatro-emo" class="panel">`: copia della sezione Teatro
  con id prefisso `te-` (`te-title`, `te-format`, `te-blocks`, `te-add`, `te-export`,
  `te-import`/`te-import-btn`, `te-genall`, `te-stop`, `te-run`, `te-status`,
  `te-progress`, `te-scene`/`te-scene-label`, `te-download`).
- **Template** `<template id="te-block-tpl">`: come `t-block-tpl` ma la riga voce è:
  - **Sesso**: due pulsanti `♂ Uomo` / `♀ Donna` (toggle, uno attivo).
  - **Voce**: `<select class="te-voice">` con le voci design del sesso scelto.
  - **Emozione**: `<select class="te-emotion">` con `neutro` + `SELECTABLE_EMOTIONS`.
  - Restano: Velocità, Pausa, Istruzione libera, Battuta, azioni (su/giù/dup/rigenera/elimina),
    progress + audio clip.

### 5. app.js — fattorizzazione `makeTeatro`
Estrarre le funzioni Teatro attuali in una factory parametrica, eliminando la
duplicazione tra i due tab:

```
makeTeatro({ prefix, fillVoiceUI, readVoice })
```
- `prefix`: `"t"` | `"te"` — prefissa selettori id (`#${prefix}-...`) e classi blocco (`.${prefix}-...`).
- `fillVoiceUI(blockEl)`: popola i controlli voce del blocco.
- `readVoice(blockEl)`: ritorna `{ voice_id, emotion }`.

Dentro la factory (condiviso, parametrizzato sul prefisso): `addBlock`, `readBlock`
(usa `readVoice` + legge char/speed/instruct/pause/text/clip), `blockToApi`,
`regenBlock` (POST `/api/generate`), `genall`, `stitchScene` (POST `/api/teatro`),
export/import scena, wiring dei pulsanti.

**Istanza Teatro** (`prefix:"t"`):
- `fillVoiceUI`: riempie `.t-voice` con le voci **clone**, solo base (niente
  varianti `id|emozione`).
- `readVoice`: `{ voice_id: <select.value>, emotion: null }`.

**Istanza Teatro-Emozioni** (`prefix:"te"`):
- `fillVoiceUI`: rende i pulsanti sesso + `.te-voice` (voci design filtrate per
  `gender`) + `.te-emotion`. Click su un sesso → ripopola `.te-voice` con le voci
  design di quel sesso e seleziona la prima. Sesso default: `♂`.
- `readVoice`: `{ voice_id: <te-voice.value>, emotion: <te-emotion.value || null> }`
  (`neutro` → `null`).

`loadVoices()` popola entrambe le istanze.

## Flusso dati (invariato lato server)

Per battuta → `POST /api/generate` con `{text, voice_id, emotion, instruct, speed, format:"wav"}`.
La pipeline (`run_generation`, ramo `design`) compone `voice_description + EMOTION_PHRASES[emotion] + instruct`.
Scena → `POST /api/teatro` fa lo stitch dei clip già generati. Nessun endpoint nuovo.

## Fuori scope (YAGNI)
- Niente UI per creare/editare voci design o settare il sesso: JSON a mano, esistono
  solo `attore`/`attrice`. Si aggiunge quando servirà più di una voce per sesso.
- Niente framework di test JS (non presente nel progetto): il check di regressione
  va sul backend (`gender` in `tests/test_voices.py`).
- Nessun nuovo endpoint API: riuso `/api/generate` + `/api/teatro`.

## Rischi / note
- Qualità del sesso sulle voci design: il modello VoiceDesign interpreta il genere
  da testo italiano in modo non sempre stabile (peggio con `temperature` alto). Non è
  un bug del codice; `gender` serve solo a filtrare le voci, non a forzare il timbro.
- Le voci clone con `emotion_samples` non saranno più selezionabili come emozione in
  Teatro (scelta voluta: Teatro = cloni neutri). Restano usabili da Genera/Batch.
