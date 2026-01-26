# Guida: Generazione Audio per Lezioni di Biochimica

Questa guida spiega come usare il sistema TTS ottimizzato per lezioni di biochimica in inglese con pronuncia corretta di terminologia scientifica.

## Caratteristiche

✅ **Voce Accademica**: Tono caldo, calmo e professionale
✅ **Pronuncia Scientifica**: Gestione automatica di formule chimiche, ioni, acronimi
✅ **Pre-processing Intelligente**: Converte H2O → "H two O", Ca2+ → "calcium ion", etc.
✅ **Personalizzabile**: Aggiungi facilmente nuovi termini specifici

---

## File Coinvolti

```
TTS_M3/
├── config/
│   └── voice_config_academic_biochem_en.json    # Configurazione voce accademica
├── src/
│   ├── biochem_text_preprocessor.py             # Preprocessore terminologia
│   └── generate_biochem_lecture.py              # Script generazione audio
├── INPUT/
│   └── biochemistry_sample.txt                  # Esempio testo lezione
└── docs/
    └── BIOCHEMISTRY_TTS_GUIDE.md                # Questa guida
```

---

## Configurazione Voce

Il file `config/voice_config_academic_biochem_en.json` contiene:

```json
{
  "language": "English",
  "voice_description": "Mature academic voice with warm and calm tone, clear and precise articulation, measured pace for educational content, authoritative yet approachable delivery, perfect for scientific lectures and technical explanations",
  "output_format": "wav",
  "sample_rate": 24000
}
```

**Caratteristiche della voce**:
- Tono maturo e professionale
- Caldo e calmo
- Articolazione chiara e precisa
- Ritmo misurato per contenuti didattici
- Autorevole ma accessibile

---

## Terminologia Supportata

### Formule Chimiche
| Originale | Pronuncia |
|-----------|-----------|
| H2O | H two O |
| CO2 | C O two |
| O2 | O two |
| ATP | A T P |
| NADH | N A D H |
| NAD+ | N A D plus |
| FADH2 | F A D H two |
| CoA | Coenzyme A |

### Ioni
| Originale | Pronuncia |
|-----------|-----------|
| Ca2+ | calcium ion |
| Mg2+ | magnesium ion |
| Na+ | sodium ion |
| K+ | potassium ion |
| Fe2+ | ferrous ion |
| Fe3+ | ferric ion |
| H+ | proton |
| Cl- | chloride ion |

### Acronimi
| Originale | Pronuncia |
|-----------|-----------|
| DNA | D N A |
| RNA | R N A |
| mRNA | messenger R N A |
| tRNA | transfer R N A |
| pH | P H |
| pKa | P K A |
| PCR | P C R |

### Aminoacidi (codici 3 lettere)
| Originale | Pronuncia |
|-----------|-----------|
| Ala | Alanine |
| Cys | Cysteine |
| Gly | Glycine |
| His | Histidine |
| ... | ... |

### Unità di Misura
| Originale | Pronuncia |
|-----------|-----------|
| mM | millimolar |
| μM | micromolar |
| kDa | kilodaltons |
| °C | degrees Celsius |
| mg/mL | milligrams per milliliter |

---

## Utilizzo Base

### 1. Generazione Audio da File di Testo

```bash
python src/generate_biochem_lecture.py \
    -i INPUT/biochemistry_sample.txt \
    -o OUTPUT/lecture_01.wav
```

### 2. Con Configurazione Personalizzata

```bash
python src/generate_biochem_lecture.py \
    -i INPUT/my_lecture.txt \
    -o OUTPUT/my_lecture.wav \
    -c config/voice_config_academic_biochem_en.json
```

### 3. Preview del Preprocessing (Senza Generare Audio)

Per vedere come verrà processato il testo:

```bash
python src/generate_biochem_lecture.py \
    -i INPUT/biochemistry_sample.txt \
    -o dummy.wav \
    --preview-preprocessing
```

### 4. Disabilitare Preprocessing

Se preferisci usare il testo così com'è:

```bash
python src/generate_biochem_lecture.py \
    -i INPUT/my_lecture.txt \
    -o OUTPUT/my_lecture.wav \
    --no-preprocess
```

---

## Utilizzo Avanzato

### Aggiungere Terminologia Personalizzata

Crea uno script Python personalizzato:

```python
from biochem_text_preprocessor import BiochemTextPreprocessor
from generate_biochem_lecture import generate_biochem_lecture

# Termini specifici per la tua lezione
custom_terms = {
    "CRISPR": "crisper",
    "Cas9": "cas nine",
    "sgRNA": "S G R N A",
    "PAM": "P A M",
}

# Genera audio con termini custom
generate_biochem_lecture(
    input_text="INPUT/crispr_lecture.txt",
    output_path="OUTPUT/crispr_lecture.wav",
    custom_mappings=custom_terms
)
```

### Uso Programmatico del Preprocessore

```python
from biochem_text_preprocessor import BiochemTextPreprocessor

preprocessor = BiochemTextPreprocessor()

text = "The reaction produces ATP and NADH using Ca2+ ions at pH 7.4"
processed = preprocessor.preprocess(text)

print(processed)
# Output: "The reaction produces A T P and N A D H using calcium ion ions at P H 7.4"
```

### Aggiungere Nuove Categorie di Termini

```python
preprocessor = BiochemTextPreprocessor()

# Enzimi specifici
enzyme_terms = {
    "RuBisCO": "rubisco",
    "DNA pol III": "D N A polymerase three",
    "Taq": "tack",
}

preprocessor.add_custom_mappings(enzyme_terms, category="custom")
```

---

## Esempi di Testo Processato

### Input Originale
```
The Km value is 10^-5 M. Ca2+ activates the enzyme, producing ATP from ADP.
The reaction requires NADH and H2O at pH 7.4.
```

### Output Processato
```
The K M value is 10 to the power of negative 5 molar. calcium ion activates
the enzyme, producing A T P from A D P. The reaction requires N A D H and
H two O at P H 7.4.
```

---

## Test del Sistema

Esegui il test del preprocessore:

```bash
cd src
python biochem_text_preprocessor.py
```

Output atteso:
```
=== Biochemical Text Preprocessor Test ===

Test 1:
Original:  The reaction requires ATP and Mg2+ ions at pH 7.4.
Processed: The reaction requires A T P and magnesium ion ions at P H 7.4.

Test 2:
Original:  Ca2+ activates the enzyme, while H2O acts as a substrate.
Processed: calcium ion activates the enzyme, while H two O acts as a substrate.
...
```

---

## Workflow Completo

### Passo 1: Prepara il Testo
Crea un file `.txt` nella cartella `INPUT/` con il testo della lezione.

### Passo 2: (Opzionale) Preview Preprocessing
```bash
python src/generate_biochem_lecture.py -i INPUT/my_lecture.txt -o dummy.wav --preview-preprocessing
```

### Passo 3: Genera Audio
```bash
python src/generate_biochem_lecture.py -i INPUT/my_lecture.txt -o OUTPUT/my_lecture.wav
```

### Passo 4: Verifica Output
L'audio generato sarà salvato in `OUTPUT/my_lecture.wav`

---

## Ottimizzazione per Lezioni Lunghe

Per lezioni molto lunghe (>5000 parole), considera di:

1. **Dividere in Capitoli**: Genera audio separati per ogni sezione
2. **Usare Batch Processing**: Elabora più file in sequenza
3. **Streaming Mode**: Il modello supporta streaming per ridurre latenza

### Esempio Script Batch

```python
import os
from pathlib import Path
from generate_biochem_lecture import generate_biochem_lecture

input_dir = Path("INPUT/lectures/")
output_dir = Path("OUTPUT/lectures/")

for txt_file in input_dir.glob("*.txt"):
    output_file = output_dir / txt_file.with_suffix('.wav').name
    print(f"Processing: {txt_file.name}")

    generate_biochem_lecture(
        input_text=str(txt_file),
        output_path=str(output_file)
    )
```

---

## Risoluzione Problemi

### Problema: Terminologia Non Riconosciuta

**Soluzione**: Aggiungi il termine al dizionario custom:

```python
custom_terms = {
    "MyProtein": "my protein",
    "XYZ123": "X Y Z one two three"
}
```

### Problema: Pronuncia Innaturale di Numeri

**Soluzione**: Scrivi i numeri in forma estesa nel testo originale:
- Invece di "pH 7.4" → "pH seven point four"
- Il preprocessore gestisce automaticamente esponenti: 10^-7 → "10 to the power of negative 7"

### Problema: Voce Troppo Veloce/Lenta

**Soluzione**: Modifica la voice description in `voice_config_academic_biochem_en.json`:
- Più lenta: "slow and deliberate pace"
- Più veloce: "moderate to quick pace"

---

## Personalizzazione Voce

Puoi creare varianti della configurazione vocale:

### Voce Più Formale
```json
{
  "voice_description": "Distinguished academic voice, formal and authoritative tone, slow deliberate pace, impeccable diction, suitable for advanced graduate lectures"
}
```

### Voce Più Accessibile
```json
{
  "voice_description": "Friendly academic voice, warm and encouraging tone, clear articulation, conversational yet professional, perfect for introductory courses"
}
```

### Voce Femminile Accademica
```json
{
  "voice_description": "Mature female academic voice, warm and engaging tone, clear and precise delivery, measured pace with natural inflection, authoritative yet approachable"
}
```

---

## Riferimenti Rapidi

### Comandi Essenziali

```bash
# Generazione base
python src/generate_biochem_lecture.py -i INPUT/file.txt -o OUTPUT/file.wav

# Preview preprocessing
python src/generate_biochem_lecture.py -i INPUT/file.txt -o dummy.wav --preview-preprocessing

# Test preprocessore
python src/biochem_text_preprocessor.py
```

### File di Configurazione
- Voce: `config/voice_config_academic_biochem_en.json`
- Preprocessore: `src/biochem_text_preprocessor.py`
- Script generazione: `src/generate_biochem_lecture.py`

---

## Note Finali

- Il preprocessing è **case-sensitive**: ATP ≠ atp
- Usa **word boundaries**: "H2O" viene riconosciuto, "H2Otest" no
- La voce è ottimizzata per **contenuti didattici**, non per conversazioni
- Il modello funziona meglio con **frasi complete e ben strutturate**

Per ulteriori personalizzazioni, consulta il codice sorgente o modifica i dizionari in `biochem_text_preprocessor.py`.
