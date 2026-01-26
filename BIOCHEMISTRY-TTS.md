# Web App Standalone per Sistema TTS con Interfaccia Grafica

## Panoramica

Questo documento esplora le opzioni per creare un'applicazione web standalone con interfaccia grafica per il sistema TTS basato su Qwen3-TTS, con particolare attenzione alla gestione di terminologia tecnica e scientifica.

---

## Opzioni Architetturali

### **Opzione 1: Web App Locale (Python Backend + HTML Frontend)** ⭐ CONSIGLIATO

**Architettura**:
- **Backend**: Flask/FastAPI che wrappa il modello Qwen3-TTS
- **Frontend**: HTML/CSS/JavaScript standalone
- **Comunicazione**: REST API o WebSocket

**Vantaggi**:
- Accesso diretto al modello già configurato
- Nessuna dipendenza da servizi esterni
- Funziona completamente offline
- Massima personalizzazione
- Separazione pulita frontend/backend

**Svantaggi**:
- Richiede server Python in esecuzione
- Non è un "singolo file HTML"
- Setup iniziale leggermente più complesso

**Tempo stimato**: 8-10 ore totali
```
Step 1: Backend API (2-3 ore)
  ├─ FastAPI server con endpoint generazione
  ├─ Gestione upload file
  ├─ Integrazione preprocessing biochimica esistente
  └─ Streaming audio response

Step 2: Frontend Base (2 ore)
  ├─ Layout responsive HTML/CSS
  ├─ Form configurazione vocale
  └─ Text editor con evidenziazione

Step 3: Funzionalità Avanzate (3 ore)
  ├─ Voice preset manager (salvataggio/caricamento profili)
  ├─ Dizionario terminologia tecnica editabile
  ├─ Drag & drop file
  └─ Audio player integrato con controlli

Step 4: Polish & Testing (1 ora)
  ├─ Styling finale
  ├─ Error handling robusto
  └─ Documentazione uso
```

**Stack Tecnologico Proposto**:
```python
# Backend
- FastAPI (moderno, async, documentazione auto-generata)
- Uvicorn (server ASGI)
- python-multipart (upload file)
- Integrazione con qwen-tts esistente

# Frontend
- HTML5 + CSS3 (Tailwind CSS o Bootstrap per styling rapido)
- Vanilla JavaScript o Alpine.js (leggero)
- Fetch API per chiamate backend
- Web Audio API per player
```

---

### **Opzione 2: Estensione della Web UI Demo Esistente** 🚀 PIÙ VELOCE

**Architettura**:
- Modificare il comando `qwen-tts-demo` esistente
- Aggiungere template HTML personalizzati
- Estendere funzionalità Gradio

**Vantaggi**:
- Implementazione rapidissima
- Server già funzionante
- Zero configurazione aggiuntiva
- Interfaccia Gradio già ottimizzata

**Svantaggi**:
- Limitata personalizzazione UI
- Dipendenza da Gradio
- Meno controllo su layout/styling
- Difficile implementare funzionalità complesse

**Tempo stimato**: 3-4 ore totali
```
Step 1: Analisi demo esistente (30 min)
  └─ Studiare codice sorgente qwen-tts-demo

Step 2: Customizzazione UI (1-2 ore)
  ├─ Modificare componenti Gradio
  ├─ Aggiungere tab per configurazioni
  └─ Integrare upload file

Step 3: Aggiunta pannello competenze (1 ora)
  ├─ Textarea per dizionario terminologia
  └─ Checkbox per preprocessing scientifico

Step 4: Integrazione preprocessing (1 ora)
  └─ Collegare script biochem esistente
```

**Note**:
- Richiede modifica del package `qwen-tts` o fork locale
- Meno flessibile per evoluzioni future

---

### **Opzione 3: Electron App** 💎 PIÙ PROFESSIONALE

**Architettura**:
- Electron per packaging app desktop
- Python backend integrato (tramite child process)
- Frontend moderno (React/Vue/Svelte)

**Vantaggi**:
- App desktop nativa multi-piattaforma
- UI moderna e professionale
- Distribuzione facile (singolo installer)
- Esperienza utente premium
- Icona applicazione, menu nativi, etc.

**Svantaggi**:
- Complessità significativamente maggiore
- Dimensione app più grande
- Richiede conoscenza JavaScript framework
- Packaging complesso

**Tempo stimato**: 12-16 ore (1-2 giorni full-time)
```
Step 1: Setup Electron + Python Bridge (3-4 ore)
  ├─ Configurazione Electron
  ├─ Python subprocess manager
  ├─ IPC (Inter-Process Communication)
  └─ Packaging Python environment

Step 2: UI Moderna con Framework (4-5 ore)
  ├─ Setup React/Vue
  ├─ Design system
  ├─ Componenti UI
  └─ State management

Step 3: Integrazione Backend (2-3 ore)
  ├─ Bridge Electron-Python
  ├─ File system access
  └─ Audio playback

Step 4: Packaging & Distribution (3-4 ore)
  ├─ Electron builder config
  ├─ Bundle Python + modelli
  ├─ Testing cross-platform
  └─ Creazione installer
```

**Stack Tecnologico**:
```javascript
// Frontend
- Electron
- React/Vue 3 + TypeScript
- Tailwind CSS
- Zustand/Pinia (state management)

// Backend Integration
- Python subprocess (pythonshell)
- FastAPI backend embedded
- electron-builder (packaging)
```

---

### **Opzione 4: Progressive Web App (PWA)** 🌐 FUTURISTICA

**Architettura**:
- Backend FastAPI cloud-hosted O locale
- Frontend PWA installabile
- Service Worker per offline

**Vantaggi**:
- Installabile come app nativa
- Funziona su mobile/tablet/desktop
- Aggiornamenti automatici
- Nessun app store

**Svantaggi**:
- Richiede hosting per backend (o server locale)
- Limitazioni browser
- Modello TTS rimane su server

**Tempo stimato**: 10-12 ore
```
Step 1: Backend API (2-3 ore)
  └─ Come Opzione 1

Step 2: PWA Frontend (4-5 ore)
  ├─ Manifest.json
  ├─ Service Worker
  ├─ Offline capabilities
  └─ Responsive design

Step 3: Installabilità (2 ore)
  ├─ Icons set
  ├─ Splash screens
  └─ Desktop integration

Step 4: Testing (2 ore)
  └─ Cross-device testing
```

---

## Funzionalità Dettagliate dell'Applicazione

Indipendentemente dall'opzione scelta, l'interfaccia includerebbe:

### **1. Pannello Configurazione Audio**
```
┌─────────────────────────────────────┐
│ ⚙️ Configurazione Audio             │
├─────────────────────────────────────┤
│ Lingua:      [▼ Italian         ]   │
│ Formato:     [▼ WAV             ]   │
│ Sample Rate: [▼ 24000 Hz       ]   │
│ Output Dir:  [📁 OUTPUT/        ]   │
└─────────────────────────────────────┘
```

### **2. Area Testo Input** 📝
```
┌─────────────────────────────────────┐
│ 📄 Testo da Convertire              │
├─────────────────────────────────────┤
│ [Carica File] [Drag & Drop Area]    │
│                                     │
│ ┌─────────────────────────────────┐ │
│ │ Il ciclo di Krebs, noto anche   │ │
│ │ come ciclo dell'acido citrico... │ │
│ │                                 │ │
│ │ (Editor con syntax highlight)   │ │
│ └─────────────────────────────────┘ │
│                                     │
│ Caratteri: 1,234 | Parole: 189     │
└─────────────────────────────────────┘
```

### **3. Voice Design Panel** 🎙️
```
┌─────────────────────────────────────┐
│ 🎤 Design Voce                      │
├─────────────────────────────────────┤
│ Preset: [▼ Seleziona...         ]   │
│         - Professore IT Biochimica  │
│         - Narratore EN Professionale│
│         - Voce Giovane Energica     │
│         - [+ Crea Nuovo Preset]     │
│                                     │
│ Descrizione Voce:                   │
│ ┌─────────────────────────────────┐ │
│ │ Voce maschile matura, tono      │ │
│ │ professionale e rassicurante,   │ │
│ │ ritmo moderato                  │ │
│ └─────────────────────────────────┘ │
│                                     │
│ [💾 Salva Preset] [🗑️ Elimina]     │
└─────────────────────────────────────┘
```

### **4. Pannello Competenze Tecniche** ⭐ INNOVATIVO
```
┌─────────────────────────────────────┐
│ 🔬 Competenze Tecniche              │
├─────────────────────────────────────┤
│ Modalità: ☑️ Preprocessing Scientifico│
│                                     │
│ Disciplina: [▼ Biochimica       ]   │
│             - Biochimica            │
│             - Chimica Organica      │
│             - Medicina              │
│             - Fisica                │
│             - Matematica            │
│             - [+ Personalizzato]    │
│                                     │
│ Dizionario Pronuncia:               │
│ ┌─────────────────────────────────┐ │
│ │ ATP → A-T-P                     │ │
│ │ NADH → NAD-H                    │ │
│ │ CoA → Co-A                      │ │
│ │ acetil-CoA → acetil Co-A        │ │
│ │ [+ Aggiungi Regola]             │ │
│ └─────────────────────────────────┘ │
│                                     │
│ [📋 Importa Dict] [💾 Esporta]      │
│ [👁️ Preview Preprocessing]          │
└─────────────────────────────────────┘
```

### **5. Controlli Generazione** ▶️
```
┌─────────────────────────────────────┐
│ ▶️ Generazione Audio                │
├─────────────────────────────────────┤
│ [🎬 GENERA AUDIO]                   │
│                                     │
│ Progress: ████████░░░░░ 60%         │
│ Status: Generating audio chunks...  │
│                                     │
│ ┌─────────────────────────────────┐ │
│ │ 🔊 Audio Player                 │ │
│ │ ▶️ ⏸️ ⏹️  [───────────] 00:00   │ │
│ │                                 │ │
│ │ output_20260126_143022.wav      │ │
│ │ [⬇️ Download] [🔄 Rigenera]     │ │
│ └─────────────────────────────────┘ │
└─────────────────────────────────────┘
```

### **6. Storia Generazioni** 📚
```
┌─────────────────────────────────────┐
│ 📜 Storia Generazioni               │
├─────────────────────────────────────┤
│ ┌─────────────────────────────────┐ │
│ │ 📄 biochemistry_lecture_01.wav  │ │
│ │    26/01/2026 14:30 | 2.3 MB   │ │
│ │    [▶️] [⬇️] [🔄] [🗑️]          │ │
│ ├─────────────────────────────────┤ │
│ │ 📄 krebs_cycle.wav              │ │
│ │    26/01/2026 12:15 | 1.8 MB   │ │
│ │    [▶️] [⬇️] [🔄] [🗑️]          │ │
│ └─────────────────────────────────┘ │
│                                     │
│ [🗂️ Apri Cartella OUTPUT]          │
└─────────────────────────────────────┘
```

---

## Confronto Rapido Opzioni

| Caratteristica | Web App Locale | Demo Estesa | Electron App | PWA |
|----------------|----------------|-------------|--------------|-----|
| **Tempo sviluppo** | 8-10 ore | 3-4 ore | 12-16 ore | 10-12 ore |
| **Complessità** | Media | Bassa | Alta | Media-Alta |
| **Personalizzazione** | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **UX Professionale** | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Offline** | ✅ | ✅ | ✅ | ⚠️ Parziale |
| **Distribuzione** | Script Python | Script Python | Installer | URL |
| **Manutenzione** | Media | Bassa | Alta | Media |
| **Mobile-friendly** | ⭐⭐⭐ | ⭐⭐ | ❌ | ⭐⭐⭐⭐⭐ |
| **Dipendenze** | Python runtime | Python + Gradio | Bundled | Python server |

---

## Domande Chiave per Decidere

Prima di procedere con l'implementazione, considera queste domande:

### **1. Priorità**
- ⚡ Velocità implementazione → **Demo Estesa**
- 🎯 Bilanciamento qualità/tempo → **Web App Locale**
- 💎 Massima qualità/professionalità → **Electron App**
- 📱 Accessibilità multi-device → **PWA**

### **2. Uso Previsto**
- Solo personale → Qualsiasi opzione
- Distribuzione a colleghi → **Electron** o **Web App Locale**
- Accesso remoto → **PWA**

### **3. Pannello Competenze Tecniche**
Oltre alla biochimica, altre discipline da supportare?
- Medicina (farmaci, patologie, anatomia)
- Chimica Organica (nomenclatura IUPAC)
- Fisica (formule, costanti)
- Matematica (simboli, teoremi)
- **→ Influisce sulla complessità del dizionario**

### **4. Preset Vocali**
Quanti profili voce utilizzerai regolarmente?
- 2-3 → Semplice dropdown
- 5-10 → Gestione avanzata con categorie
- 10+ → Database preset con ricerca
- **→ Influisce su design UI pannello voce**

### **5. Batch Processing**
- Un file alla volta → UI più semplice
- Elaborazione multipla → Queue manager necessario
- **→ Influisce su architettura backend**

### **6. Evoluzione Futura**
Funzionalità future previste?
- Voice cloning con campioni audio
- Integrazione con altri servizi
- API per automazione
- **→ Influisce su scelta architetturale**

---

## Raccomandazione Finale

**Per uso personale/piccolo team con focus su qualità**:
→ **Opzione 1: Web App Locale**

**Motivazioni**:
- Tempo ragionevole (8-10 ore = 1-2 giornate)
- Massima flessibilità per terminologia tecnica
- Facile manutenzione e aggiornamenti
- Buon bilanciamento qualità/complessità
- Possibilità di evolvere verso Electron in futuro

**Quick Start consigliato**:
- Opzione 2 (Demo Estesa) per prototipo rapido
- Poi migrare a Opzione 1 se soddisfacente

---

## Prossimi Passi

Quando deciderai di procedere:

1. **Comunicami**:
   - Opzione scelta
   - Risposte alle domande chiave sopra
   - Eventuali funzionalità aggiuntive desiderate

2. **Preparazione**:
   - Verificare dipendenze installate
   - Decidere struttura directory progetto
   - Preparare esempi testo per testing

3. **Implementazione**:
   - Seguiremo step-by-step il piano dell'opzione scelta
   - Testing incrementale dopo ogni fase
   - Documentazione d'uso finale

---

## Note Tecniche Aggiuntive

### **Gestione Terminologia Scientifica**

Il sistema di preprocessing per terminologia tecnica può essere implementato con:

```python
# Struttura dizionario esempio
{
  "biochimica": {
    "ATP": "A-T-P",
    "NADH": "NAD-H",
    "CoA": "Co-A",
    "acetil-CoA": "acetil Co-A",
    "ciclo di Krebs": "ciclo di Krebs",  # nessuna modifica
    # pattern regex avanzati
    r"(\d+)kDa": r"\1 kilo-dalton",
  },
  "chimica_organica": {
    "CH3COOH": "C-H-3 C-O-O-H",
    # ...
  }
}
```

### **Storage Configurazioni**

- Preset vocali: JSON in `config/voice_presets.json`
- Dizionari: YAML in `config/dictionaries/`
- Settings app: `config/app_settings.json`
- Storia generazioni: SQLite locale o JSON

### **Ottimizzazione Performance**

- Caching modello in memoria (già caricato)
- Generazione asincrona con progress updates
- Compressione audio on-the-fly
- Lazy loading frontend components

---

**Data documento**: 26 Gennaio 2026
**Versione**: 1.0
**Per domande**: Rivedi questo documento e comunica l'opzione scelta con risposte alle domande chiave.
