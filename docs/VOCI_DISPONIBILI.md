# Voci Disponibili per Voice Cloning

Questo documento elenca tutte le voci clonate disponibili nel sistema con le loro caratteristiche.

---

## 📋 Voci Attive

### 1. Gazzolo

**File Audio**: `VOICE_SAMPLES/gazzolo_01.wav`
**Configurazione**: `config/clone_gazzolo.json`

**Caratteristiche Vocali**:
- **Lingua**: Italiano
- **Genere**: Maschile
- **Tono**: Professionale, caldo, autorevole
- **Ritmo**: Moderato
- **Durata campione**: 5.7 secondi
- **Qualità**: Alta (estratto da video)

**Trascrizione di riferimento**:
> "Grazie. Allora, oggi parleremo di biochimica strutturale, concentrandoci sulla struttura delle proteine."

**Utilizzo**:
```bash
# Genera audio con voce Gazzolo
python src/generate_cloned_audio.py -i INPUT/testo.txt -c config/clone_gazzolo.json -o OUTPUT/audio.wav

# Batch processing
python src/batch_clone_process.py -c config/clone_gazzolo.json
```

**Note**:
- Ideale per contenuti educativi e professionali
- Ottima chiarezza articolatoria
- Perfetta per lezioni di biochimica/scienze

---

## 📁 Come Aggiungere Nuove Voci

### 1. Prepara il campione audio
```bash
# Estrai da video
python src/extract_audio_from_video.py -i video.mp4 -o VOICE_SAMPLES/nome_voce.wav --start 10 --duration 5

# Ottimizza (opzionale)
python src/prepare_voice_sample.py -i VOICE_SAMPLES/raw.wav -o VOICE_SAMPLES/nome_voce.wav
```

### 2. Crea file di configurazione
Copia il template e personalizza:
```bash
cp config/templates/clone_config_template.json config/clone_nuova_voce.json
```

Modifica i campi:
- `prompt_speech_path`: Path al file audio
- `ref_text`: Trascrizione ESATTA dell'audio
- `language`: Lingua del testo da sintetizzare
- `voice_notes`: Descrizione delle caratteristiche vocali

### 3. Testa la nuova voce
```bash
python src/generate_cloned_audio.py -i INPUT/test.txt -c config/clone_nuova_voce.json -o OUTPUT/test.wav
```

### 4. Aggiungi alla lista
Modifica questo file (`docs/VOCI_DISPONIBILI.md`) aggiungendo la nuova voce nella sezione "Voci Attive".

---

## 🎯 Convenzioni di Naming

### File Audio
```
VOICE_SAMPLES/nome_descrittivo_NN.wav
```
- `nome_descrittivo`: Nome speaker o descrizione breve
- `_NN`: Numero progressivo se ci sono più campioni dello stesso speaker
- Esempio: `gazzolo_01.wav`, `professore_02.wav`

### File Configurazione
```
config/clone_nome_descrittivo.json
```
- Prefisso `clone_` obbligatorio
- Nome coerente con file audio
- Esempio: `clone_gazzolo.json`, `clone_professore.json`

---

## 📊 Statistiche Campioni

| Voce | Durata | Dimensione | Formato | Qualità |
|------|--------|------------|---------|---------|
| Gazzolo | 5.7s | 342 KB | WAV mono 24kHz | Alta |

---

## 🔧 Template Disponibili

I template di configurazione si trovano in `config/templates/`:

- `clone_config_template.json` - Template base generico
- `clone_config_speaker1.json` - Esempio voce maschile italiana
- `clone_config_speaker2.json` - Esempio voce femminile italiana
- `clone_config_cross_lingual.json` - Esempio cross-lingual (voce EN → testo IT)

---

## 📚 Risorse Correlate

- **Guida completa voice cloning**: [docs/VOICE_CLONING_GUIDE.md](VOICE_CLONING_GUIDE.md)
- **Esempi pratici**: [EXAMPLES.md](../EXAMPLES.md)
- **Documentazione tecnica**: [CLAUDE.md](../CLAUDE.md)
- **Gestione campioni audio**: [VOICE_SAMPLES/README.md](../VOICE_SAMPLES/README.md)

---

## ⚙️ Script Utili

```bash
# Lista tutti i campioni disponibili
python src/list_voice_samples.py

# Verifica qualità campione
python src/prepare_voice_sample.py -i VOICE_SAMPLES/voce.wav --suggest

# Estrai da video batch
python src/extract_audio_from_video.py -i videos/ -o VOICE_SAMPLES/extracted/
```

---

**Ultimo aggiornamento**: 2026-02-01
**Voci totali**: 1
