# Configurazioni Vocali TTS

Questa directory contiene file di configurazione per diverse voci organizzate per lingua e tipologia di narratore.

## Indice

- [Configurazioni Italiano](#-configurazioni-italiano)
  - [Narratori Maschili](#narratore-maschile)
  - [Narratrici Femminili](#narratrice-femminile)
- [Configurazioni Inglese](#-configurazioni-inglese)
- [Linee Guida Voice Description](#-linee-guida-per-voice-description)
- [Parametri Tecnici](#️-parametri-tecnici)

---

## Struttura del File di Configurazione

```json
{
  "language": "Italian",
  "voice_description": "Descrizione dettagliata della voce desiderata",
  "output_format": "wav",
  "sample_rate": 24000
}
```

### Parametri

- **language**: Lingua del parlato
  - Valori supportati: `Italian`, `English`, `Chinese`, `Japanese`, `Korean`, `German`, `French`, `Russian`, `Portuguese`, `Spanish`
  - Consiglio: specificare sempre esplicitamente invece di usare "Auto"

- **voice_description**: Descrizione testuale della voce
  - Sii specifico e dettagliato
  - Includi: genere, età approssimativa, tono, velocità, caratteristiche
  - Esempi:
    - "Voce maschile matura, tono caldo e professionale, ritmo moderato"
    - "Voce femminile giovane, entusiasta e amichevole, articolazione chiara"
    - "Voce neutra, tono formale e autorevole, ritmo lento e chiaro"

- **output_format**: Formato file audio
  - `wav`: Formato lossless (consigliato)
  - `mp3`: Formato compresso (richiede pydub e ffmpeg)

- **sample_rate**: Frequenza di campionamento
  - Default: 24000 Hz
  - Il modello genera nativamente a 12 kHz (12.5 fps)

---

## 🇮🇹 Configurazioni Italiano

### Narratore Maschile

#### 1. Narratore Professionale (Generale)
**File**: `voice_config_narratore_professionale.json`

```json
{
  "language": "Italian",
  "voice_description": "Voce maschile baritonale, tono caldo e rassicurante, ritmo calmo e rilassato, articolazione chiara e naturale, timbro profondo e morbido, ideale per narrazione",
  "output_format": "wav",
  "sample_rate": 24000
}
```

**Ideale per**: Audiolibri, narrazione generale, podcast narrativi

---

#### 2. Narratore Intimo
**File**: `voice_config_narratore_intimo.json`

```json
{
  "language": "Italian",
  "voice_description": "Voce maschile matura con registro baritonale, timbro caldo e avvolgente, parlata pacata e riflessiva, tono confidenziale ma professionale",
  "output_format": "wav",
  "sample_rate": 24000
}
```

**Ideale per**: Poesia, meditazioni guidate, contenuti riflessivi, storytelling intimo

---

#### 3. Narratore Documentaristico
**File**: `voice_config_narratore_documentaristico.json`

```json
{
  "language": "Italian",
  "voice_description": "Voce maschile profonda e autorevole, tono equilibrato e calmo, dizione impeccabile, calore naturale, perfetta per narrazione documentaristica",
  "output_format": "wav",
  "sample_rate": 24000
}
```

**Ideale per**: Documentari, contenuti educativi, saggistica, divulgazione scientifica

---

#### 4. Narratore Energico
**File**: `voice_config_narratore_energico.json`

```json
{
  "language": "Italian",
  "voice_description": "Voce maschile dinamica e coinvolgente, tono vivace ma controllato, ritmo moderato-veloce, articolazione precisa, timbro chiaro e penetrante",
  "output_format": "wav",
  "sample_rate": 24000
}
```

**Ideale per**: Thriller, azione, contenuti motivazionali, narrazione giovane

---

### Narratrice Femminile

#### 1. Narratrice Professionale
**File**: `voice_config_narratrice_professionale.json`

```json
{
  "language": "Italian",
  "voice_description": "Voce femminile matura, tono caldo e rassicurante, articolazione chiara e precisa, ritmo moderato e piacevole, timbro equilibrato e naturale",
  "output_format": "wav",
  "sample_rate": 24000
}
```

**Ideale per**: Audiolibri, narrazione generale, contenuti professionali

---

#### 2. Narratrice Giovane ed Energica
**File**: `voice_config_narratrice_giovane.json`

```json
{
  "language": "Italian",
  "voice_description": "Voce femminile giovane, tono amichevole e vivace, energia positiva, articolazione chiara, ritmo scorrevole e coinvolgente",
  "output_format": "wav",
  "sample_rate": 24000
}
```

**Ideale per**: Contenuti young adult, narrativa contemporanea, podcast lifestyle

---

#### 3. Narratrice Matura ed Elegante
**File**: `voice_config_narratrice_elegante.json`

```json
{
  "language": "Italian",
  "voice_description": "Voce femminile matura ed elegante, tono sofisticato e raffinato, dizione impeccabile, ritmo calmo e misurato, timbro ricco e profondo",
  "output_format": "wav",
  "sample_rate": 24000
}
```

**Ideale per**: Narrativa classica, saggistica, contenuti culturali, poesia

---

## 🇬🇧 Configurazioni Inglese

### Male Narrator

#### 1. Professional Narrator
**File**: `voice_config_narrator_professional_en.json`

```json
{
  "language": "English",
  "voice_description": "Mature male voice with warm baritone tone, calm and reassuring delivery, clear articulation, smooth and natural timber, perfect for storytelling",
  "output_format": "wav",
  "sample_rate": 24000
}
```

**Best for**: Audiobooks, general narration, podcasts

---

#### 2. Documentary Narrator
**File**: `voice_config_narrator_documentary_en.json`

```json
{
  "language": "English",
  "voice_description": "Deep authoritative male voice, balanced and calm tone, impeccable diction, natural warmth, BBC-style documentary narration",
  "output_format": "wav",
  "sample_rate": 24000
}
```

**Best for**: Documentaries, educational content, non-fiction

---

### Female Narrator

#### 1. Professional Narrator
**File**: `voice_config_narrator_professional_female_en.json`

```json
{
  "language": "English",
  "voice_description": "Mature female voice, warm and reassuring tone, clear and precise articulation, moderate and pleasant pace, balanced natural timber",
  "output_format": "wav",
  "sample_rate": 24000
}
```

**Best for**: Audiobooks, professional content, general narration

---

#### 2. Energetic Narrator
**File**: `voice_config_narrator_energetic_female_en.json`

```json
{
  "language": "English",
  "voice_description": "Young female voice, friendly and enthusiastic tone, positive energy, clear articulation, engaging and flowing pace",
  "output_format": "wav",
  "sample_rate": 24000
}
```

**Best for**: Young adult content, contemporary fiction, lifestyle podcasts

---

## 📋 Linee Guida per Voice Description

### Elementi Chiave da Includere

1. **Genere e Maturità**: "Voce maschile/femminile giovane/matura"
2. **Registro Vocale**: "baritonale/tenore/soprano/contralto"
3. **Tono Emotivo**: "caldo/freddo/rassicurante/energico/professionale"
4. **Ritmo**: "calmo/veloce/moderato/rilassato/dinamico"
5. **Articolazione**: "chiara/precisa/naturale/impeccabile"
6. **Timbro**: "profondo/morbido/ricco/penetrante/equilibrato"
7. **Contesto d'Uso**: "ideale per narrazione/documentari/poesia"

### Esempi di Combinazioni Efficaci

**Voce Calda e Rassicurante**:
```
"tono caldo e rassicurante, timbro morbido e avvolgente, ritmo calmo"
```

**Voce Autorevole**:
```
"voce profonda e autorevole, dizione impeccabile, tono equilibrato"
```

**Voce Energica**:
```
"tono vivace e dinamico, ritmo scorrevole, energia positiva"
```

**Voce Intima**:
```
"tono confidenziale, parlata pacata e riflessiva, timbro caldo"
```

---

## 🎛️ Parametri Tecnici

### Output Format

- **wav**: Massima qualità, nessuna compressione (consigliato per produzione)
- **mp3**: Compresso, file più piccoli (usare dopo conversione da wav)

### Sample Rate

- **24000 Hz**: Default ottimale per Qwen3-TTS-12Hz
- Non modificare a meno che non ci siano esigenze specifiche

---

## 🚀 Utilizzo

### Generazione Singola
```bash
python src/generate_audio.py --input INPUT/testo.txt --config config/voice_config_narratore_professionale.json
```

### Batch Processing
```bash
python src/batch_process.py --config config/voice_config_narratrice_giovane.json
```

---

## 💡 Suggerimenti

1. **Testa Varianti**: Prova 2-3 configurazioni diverse sullo stesso testo per confrontare i risultati
2. **Usa WAV Prima**: Genera sempre in WAV per qualità massima, poi converti in MP3 se necessario
3. **Descrizioni Specifiche**: Più dettagli nella voice_description = risultati più accurati
4. **Lingua Esplicita**: Specifica sempre la lingua, non usare "Auto"
5. **Lunghezza Descrizione**: 15-25 parole è la lunghezza ideale per voice_description
6. **Test su Testo Breve**: Prima di elaborazioni batch, testa sempre su un paragrafo breve

---

## 📝 Note

- Tutte le configurazioni sono ottimizzate per MacBook Pro M3 Max
- Il modello Qwen3-TTS-12Hz-1.7B-VoiceDesign supporta 10 lingue
- La prima generazione può richiedere 1-2 secondi per caricare il modello
- Le generazioni successive sono molto più veloci in streaming mode
- Lingue supportate: Italian, English, Chinese, Japanese, Korean, German, French, Russian, Portuguese, Spanish
