# Changelog

Tutte le modifiche importanti al progetto saranno documentate in questo file.

## [1.0.0] - 2026-01-26

### Aggiunto
- ✨ Sistema TTS completo basato su Qwen3-TTS-12Hz-1.7B-VoiceDesign
- 🎤 Supporto voice design tramite descrizioni testuali
- 🇮🇹 Supporto multilingua (10 lingue: Italiano, Inglese, e altri)
- 📦 Script di elaborazione batch per multipli file
- 🚀 Ottimizzazioni specifiche per M3 Max (MPS, Flash Attention 2)
- 🎵 Output in formato WAV e MP3
- ⚙️ Sistema di configurazione JSON per voci personalizzate
- 🧪 Script di test installazione completo
- 📚 Documentazione completa:
  - README.md principale
  - QUICKSTART.md per inizio rapido
  - CLAUDE.md con dettagli tecnici
  - config/README.md per voice design
- 🛠️ Script di setup automatico (setup.sh)
- 📋 File di esempio pre-caricato

### File Principali
- `src/generate_audio.py`: Generazione audio singola
- `src/batch_process.py`: Elaborazione batch
- `test_installation.py`: Verifica installazione
- `setup.sh`: Setup automatico ambiente
- `requirements.txt`: Dipendenze Python

### Configurazioni Pre-installate
- `config/voice_config.json`: Voce maschile italiana professionale
- `config/voice_config_female.json`: Voce femminile italiana energica
- `config/voice_config_english.json`: Voce maschile inglese professionale

### Struttura Directory
```
TTS_M3/
├── INPUT/          # File .txt da convertire
├── OUTPUT/         # File audio generati
├── config/         # Configurazioni vocali
├── src/            # Codice sorgente
├── models/         # Cache modelli (auto-download)
└── docs/           # Documentazione
```

### Note Tecniche
- Richiede Python 3.12
- Ottimizzato per macOS M3 Max con 36GB RAM
- Usa Metal Performance Shaders (MPS) per GPU
- Supporto Flash Attention 2 opzionale
- Download automatico modelli al primo utilizzo (~3-5GB)

### Prestazioni Attese (M3 Max)
- Primo caricamento: ~10-20 secondi
- Generazioni successive: ~1-2 secondi per frase
- Batch processing: riutilizzo modello per massima efficienza

---

## Formato

Questo changelog segue le linee guida di [Keep a Changelog](https://keepachangelog.com/it/1.0.0/),
e il progetto aderisce al [Semantic Versioning](https://semver.org/lang/it/).

### Tipi di Modifiche
- `Aggiunto` per nuove funzionalità
- `Modificato` per cambiamenti a funzionalità esistenti
- `Deprecato` per funzionalità che saranno rimosse
- `Rimosso` per funzionalità rimosse
- `Corretto` per bug fix
- `Sicurezza` per vulnerabilità corrette
