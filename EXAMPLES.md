# Esempi Pratici - TTS_M3

Raccolta di esempi pratici pronti all'uso per vari scenari.

## 🎬 Setup Iniziale

```bash
# Clone e setup
git clone <repository-url>
cd TTS_M3
./setup.sh

# Attiva ambiente
conda activate qwen3-tts

# Verifica installazione
python test_installation.py
```

## 📝 Esempi Base

### 1. Primo Audio (Voce Default)

```bash
# Crea testo
cat > INPUT/primo_test.txt << 'EOF'
Benvenuto nel sistema di sintesi vocale. Questa è una prova della qualità audio.
EOF

# Genera
python src/generate_audio.py -i INPUT/primo_test.txt

# Risultato
ls -lh OUTPUT/primo_test.wav
```

### 2. Voce Femminile

```bash
# Crea testo
echo "Questo audio usa una voce femminile giovane ed energica." > INPUT/voce_donna.txt

# Genera con voce femminile
python src/generate_audio.py \
  -i INPUT/voce_donna.txt \
  -c config/voice_config_female.json

# Ascolta
open OUTPUT/voce_donna.wav
```

### 3. Audio in Inglese

```bash
# Crea testo inglese
cat > INPUT/english_test.txt << 'EOF'
This is a test of the English voice. The system supports multiple languages
with natural-sounding voices.
EOF

# Genera
python src/generate_audio.py \
  -i INPUT/english_test.txt \
  -c config/voice_config_english.json

# Risultato
open OUTPUT/english_test.wav
```

## 📚 Esempi Audiolibro

### Capitoli Multipli

```bash
# Crea capitoli
cat > INPUT/capitolo_01.txt << 'EOF'
Capitolo Uno: L'Inizio.
Era una mattina di primavera quando tutto ebbe inizio...
EOF

cat > INPUT/capitolo_02.txt << 'EOF'
Capitolo Due: Lo Sviluppo.
I giorni passavano lentamente, mentre la storia si dipanava...
EOF

cat > INPUT/capitolo_03.txt << 'EOF'
Capitolo Tre: La Conclusione.
Infine, dopo molte peripezie, giunse il momento della verità...
EOF

# Genera tutti i capitoli in batch
python src/batch_process.py

# Risultati
ls -lh OUTPUT/capitolo_*.wav
```

### Con Voce Specifica

```bash
# Genera tutti con voce maschile professionale
python src/batch_process.py -c config/voice_config.json

# O con voce femminile
python src/batch_process.py -c config/voice_config_female.json
```

## 🎙️ Esempi Podcast

### Intro + Contenuto + Outro

```bash
# Intro (voce maschile)
cat > INPUT/podcast_intro.txt << 'EOF'
Benvenuti al nostro podcast settimanale. Oggi parleremo di intelligenza
artificiale e sintesi vocale.
EOF

python src/generate_audio.py \
  -i INPUT/podcast_intro.txt \
  -c config/voice_config.json \
  -o OUTPUT/01_intro.wav

# Contenuto principale (voce femminile)
cat > INPUT/podcast_contenuto.txt << 'EOF'
La tecnologia di sintesi vocale ha fatto enormi progressi negli ultimi anni.
I modelli moderni possono produrre voci incredibilmente naturali.
EOF

python src/generate_audio.py \
  -i INPUT/podcast_contenuto.txt \
  -c config/voice_config_female.json \
  -o OUTPUT/02_contenuto.wav

# Outro (voce maschile)
cat > INPUT/podcast_outro.txt << 'EOF'
Grazie per l'ascolto. Ci sentiamo alla prossima settimana!
EOF

python src/generate_audio.py \
  -i INPUT/podcast_outro.txt \
  -c config/voice_config.json \
  -o OUTPUT/03_outro.wav

# Lista risultati
ls -lh OUTPUT/0*.wav
```

## 🌍 Esempi Multilingua

### Italiano + Inglese

```bash
# Sezione italiana
cat > INPUT/parte_italiana.txt << 'EOF'
Questa è la sezione in italiano del nostro progetto multilingua.
EOF

python src/generate_audio.py \
  -i INPUT/parte_italiana.txt \
  -c config/voice_config.json \
  -o OUTPUT/sezione_it.wav

# Sezione inglese
cat > INPUT/english_section.txt << 'EOF'
This is the English section of our multilingual project.
EOF

python src/generate_audio.py \
  -i INPUT/english_section.txt \
  -c config/voice_config_english.json \
  -o OUTPUT/section_en.wav
```

## 🎨 Voci Personalizzate

### Crea Voce Custom

```bash
# Crea nuova configurazione
cat > config/voice_config_narrator.json << 'EOF'
{
  "language": "Italian",
  "voice_description": "Voce anziana esperta, tono saggio e riflessivo, ritmo lento e cadenzato, perfetto per narrazioni",
  "output_format": "wav",
  "sample_rate": 24000
}
EOF

# Testa nuova voce
cat > INPUT/test_narrator.txt << 'EOF'
C'era una volta, in un tempo lontano, una storia che merita di essere raccontata.
EOF

python src/generate_audio.py \
  -i INPUT/test_narrator.txt \
  -c config/voice_config_narrator.json

# Ascolta risultato
open OUTPUT/test_narrator.wav
```

### Voce Energica

```bash
# Configurazione voce energica
cat > config/voice_config_energetic.json << 'EOF'
{
  "language": "Italian",
  "voice_description": "Voce giovane e dinamica, tono entusiasta ed energico, ritmo veloce, perfetto per contenuti motivazionali",
  "output_format": "wav"
}
EOF

# Test
echo "Oggi è un giorno fantastico! Pieni di energia e pronti a conquistare il mondo!" > INPUT/energetico.txt

python src/generate_audio.py \
  -i INPUT/energetico.txt \
  -c config/voice_config_energetic.json
```

## 🎵 Output MP3

### Converti in MP3

```bash
# Modifica configurazione per MP3
cat > config/voice_config_mp3.json << 'EOF'
{
  "language": "Italian",
  "voice_description": "Voce professionale, tono neutro e chiaro",
  "output_format": "mp3",
  "sample_rate": 24000
}
EOF

# Genera direttamente MP3
echo "Questo file sarà salvato in formato MP3 compresso." > INPUT/test_mp3.txt

python src/generate_audio.py \
  -i INPUT/test_mp3.txt \
  -c config/voice_config_mp3.json

# Risultato in MP3
ls -lh OUTPUT/test_mp3.mp3
```

## 📦 Batch Processing Avanzato

### Elabora Tutti, Forza Rigenerazione

```bash
# Crea multipli file
for i in {1..5}; do
  echo "Questo è il file numero $i" > INPUT/batch_$i.txt
done

# Prima elaborazione
python src/batch_process.py

# Modifica un file
echo "Questo è il file numero 3 - MODIFICATO" > INPUT/batch_3.txt

# Rigenera solo modificati (default)
python src/batch_process.py

# O forza rigenerazione di tutto
python src/batch_process.py --force
```

### Con Configurazione Custom

```bash
# Batch con voce specifica
python src/batch_process.py \
  -i INPUT \
  -o OUTPUT \
  -c config/voice_config_female.json

# Con directory custom
mkdir -p MY_INPUT MY_OUTPUT
echo "Test custom directory" > MY_INPUT/test.txt

python src/batch_process.py \
  -i MY_INPUT \
  -o MY_OUTPUT \
  -c config/voice_config.json
```

## 🔧 Workflow Completi

### Workflow 1: Serie Educativa

```bash
# Crea serie di lezioni
mkdir -p INPUT/lezioni

cat > INPUT/lezioni/lezione_01.txt << 'EOF'
Lezione Uno: Introduzione alla Fisica Quantistica.
Oggi iniziamo il nostro viaggio nel mondo affascinante della meccanica quantistica.
EOF

cat > INPUT/lezioni/lezione_02.txt << 'EOF'
Lezione Due: Il Principio di Indeterminazione.
Heisenberg ci insegnò che non possiamo conoscere simultaneamente posizione e velocità.
EOF

cat > INPUT/lezioni/lezione_03.txt << 'EOF'
Lezione Tre: L'Entanglement Quantistico.
Due particelle possono essere correlate indipendentemente dalla distanza.
EOF

# Genera tutte le lezioni
python src/batch_process.py \
  -i INPUT/lezioni \
  -o OUTPUT/lezioni \
  -c config/voice_config.json
```

### Workflow 2: Newsletter Audio

```bash
# Newsletter settimanale
cat > INPUT/newsletter_$(date +%Y%m%d).txt << 'EOF'
Buongiorno! Ecco le notizie di questa settimana.
Primo: abbiamo lanciato la nuova funzionalità di sintesi vocale.
Secondo: il numero di utenti è cresciuto del 30%.
Terzo: abbiamo in programma nuovi aggiornamenti per il mese prossimo.
Grazie per l'attenzione e buona settimana!
EOF

# Genera
python src/generate_audio.py \
  -i INPUT/newsletter_$(date +%Y%m%d).txt \
  -c config/voice_config_female.json
```

### Workflow 3: Contenuto Social

```bash
# Crea script per social media
mkdir -p INPUT/social

cat > INPUT/social/post_1.txt << 'EOF'
Ciao a tutti! Oggi vi parlo di come l'intelligenza artificiale sta
rivoluzionando il mondo della sintesi vocale.
EOF

cat > INPUT/social/post_2.txt << 'EOF'
Sapevate che è possibile generare voci realistiche usando solo
descrizioni testuali? Scopriamo come!
EOF

cat > INPUT/social/post_3.txt << 'EOF'
Volete creare contenuti audio professionali? Vi mostro gli strumenti
che uso ogni giorno!
EOF

# Genera con voce energica
python src/batch_process.py \
  -i INPUT/social \
  -o OUTPUT/social \
  -c config/voice_config_female.json
```

## 🧪 Testing e Debug

### Test Rapido Qualità

```bash
# Frase di test standard
cat > INPUT/test_qualita.txt << 'EOF'
Il test della qualità audio include consonanti, vocali, pause e intonazioni diverse.
Ascoltiamo attentamente il risultato per valutare naturalezza e chiarezza.
EOF

# Genera con voci diverse
for config in config/voice_config*.json; do
  name=$(basename "$config" .json)
  python src/generate_audio.py \
    -i INPUT/test_qualita.txt \
    -c "$config" \
    -o "OUTPUT/test_${name}.wav"
done

# Confronta risultati
ls -lh OUTPUT/test_*.wav
```

### Test Lingue

```bash
# Test tutte le lingue principali
declare -A LANGUAGES
LANGUAGES=(
  ["Italian"]="Questo è un test in italiano."
  ["English"]="This is a test in English."
  ["German"]="Dies ist ein Test auf Deutsch."
  ["French"]="Ceci est un test en français."
  ["Spanish"]="Esta es una prueba en español."
)

# Genera test per ogni lingua
for lang in "${!LANGUAGES[@]}"; do
  echo "${LANGUAGES[$lang]}" > "INPUT/test_${lang}.txt"

  # Crea config temporanea
  cat > "config/temp_${lang}.json" << EOF
{
  "language": "${lang}",
  "voice_description": "Professional neutral voice, clear and natural",
  "output_format": "wav"
}
EOF

  # Genera
  python src/generate_audio.py \
    -i "INPUT/test_${lang}.txt" \
    -c "config/temp_${lang}.json" \
    -o "OUTPUT/test_${lang}.wav"
done

# Lista risultati
ls -lh OUTPUT/test_*.wav
```

## 💡 Tips e Tricks

### Preview Veloce

```bash
# Testa voce con frase breve
echo "Test rapido voce" | \
  tee INPUT/quick_test.txt | \
  xargs -I {} python src/generate_audio.py -i INPUT/quick_test.txt && \
  open OUTPUT/quick_test.wav
```

### Cleanup Output

```bash
# Rimuovi tutti i file generati
rm OUTPUT/*.wav OUTPUT/*.mp3

# Rimuovi solo WAV
rm OUTPUT/*.wav

# Rimuovi solo MP3
rm OUTPUT/*.mp3
```

### Statistiche Batch

```bash
# Conta file processati
echo "File input: $(ls INPUT/*.txt 2>/dev/null | wc -l)"
echo "File output: $(ls OUTPUT/*.{wav,mp3} 2>/dev/null | wc -l)"

# Spazio occupato
du -sh OUTPUT/
```

## 🎓 Best Practices

### 1. Organizza per Progetto

```bash
# Struttura per progetti multipli
mkdir -p INPUT/progetto_A INPUT/progetto_B
mkdir -p OUTPUT/progetto_A OUTPUT/progetto_B

# Processa separatamente
python src/batch_process.py -i INPUT/progetto_A -o OUTPUT/progetto_A
python src/batch_process.py -i INPUT/progetto_B -o OUTPUT/progetto_B
```

### 2. Backup Configurazioni

```bash
# Crea backup configurazioni
cp -r config config_backup_$(date +%Y%m%d)

# Versionamento configurazioni
mkdir -p config/archive
cp config/voice_config_custom.json config/archive/custom_v1.json
```

### 3. Automatizzazione

```bash
# Script di automazione esempio
cat > generate_daily.sh << 'EOF'
#!/bin/bash
DATE=$(date +%Y%m%d)
INPUT_FILE="INPUT/daily_${DATE}.txt"
OUTPUT_FILE="OUTPUT/daily_${DATE}.wav"

if [ -f "$INPUT_FILE" ]; then
  python src/generate_audio.py -i "$INPUT_FILE" -o "$OUTPUT_FILE"
  echo "✓ Generato: $OUTPUT_FILE"
else
  echo "✗ File non trovato: $INPUT_FILE"
fi
EOF

chmod +x generate_daily.sh
./generate_daily.sh
```

## 🎭 Voice Cloning

### Quick Start Voice Cloning

```bash
# 1. Estrai audio da video
python src/extract_audio_from_video.py \
  -i video_intervista.mp4 \
  -o VOICE_SAMPLES/mia_voce.wav \
  --start 10 \
  --duration 5

# 2. Crea configurazione
cat > config/clone_mia_voce.json << 'EOF'
{
  "mode": "voice_clone",
  "language": "Italian",
  "prompt_speech_path": "VOICE_SAMPLES/mia_voce.wav",
  "output_format": "wav",
  "sample_rate": 24000
}
EOF

# 3. Genera audio clonato
python src/generate_cloned_audio.py \
  -i INPUT/testo.txt \
  -c config/clone_mia_voce.json \
  -o OUTPUT/audio_clonato.wav
```

### Workflow Completo da MP4

```bash
# Step 1: Estrai audio da video MP4
python src/extract_audio_from_video.py \
  -i video_lezione.mp4 \
  -o VOICE_SAMPLES/professore.wav \
  --start 30 \
  --duration 6

# Step 2: Verifica qualità campione
python src/list_voice_samples.py

# Step 3: (Opzionale) Ottimizza campione
python src/prepare_voice_sample.py \
  -i VOICE_SAMPLES/professore.wav \
  -o VOICE_SAMPLES/professore_clean.wav

# Step 4: Crea testo lezione
cat > INPUT/lezione_biochimica.txt << 'EOF'
Oggi parleremo del ciclo di Krebs e della fosforilazione ossidativa.
Il ciclo di Krebs è fondamentale per la produzione di ATP nelle cellule.
EOF

# Step 5: Genera con voice cloning
python src/generate_cloned_audio.py \
  -i INPUT/lezione_biochimica.txt \
  -c config/clone_professore.json
```

### Batch Processing con Voice Cloning

```bash
# Crea multipli file da sintetizzare
cat > INPUT/slide_01.txt << 'EOF'
Benvenuti alla prima lezione sul metabolismo cellulare.
EOF

cat > INPUT/slide_02.txt << 'EOF'
Il metabolismo si divide in catabolismo e anabolismo.
EOF

cat > INPUT/slide_03.txt << 'EOF'
Concludiamo con un riepilogo dei concetti chiave.
EOF

# Batch cloning di tutti i file
python src/batch_clone_process.py -c config/clone_professore.json

# Risultati
ls -lh OUTPUT/*_cloned.wav
```

### Cross-Lingual Cloning

```bash
# Usa voce inglese per parlare italiano
# 1. Estrai voce inglese
python src/extract_audio_from_video.py \
  -i english_video.mp4 \
  -o VOICE_SAMPLES/english_speaker.wav \
  --duration 5

# 2. Config cross-lingual
cat > config/clone_cross_lingual.json << 'EOF'
{
  "mode": "voice_clone",
  "language": "Italian",
  "prompt_speech_path": "VOICE_SAMPLES/english_speaker.wav",
  "output_format": "wav",
  "voice_notes": "Cross-lingual: voce inglese per italiano"
}
EOF

# 3. Genera testo italiano con voce inglese
cat > INPUT/testo_italiano.txt << 'EOF'
Questo testo in italiano sarà sintetizzato usando la voce inglese.
Il timbro vocale originale sarà preservato.
EOF

python src/generate_cloned_audio.py \
  -i INPUT/testo_italiano.txt \
  -c config/clone_cross_lingual.json
```

### Voice Cloning + Preprocessing Biochimica

```bash
# Genera lezione scientifica con voice cloning
cat > INPUT/lezione_atp.txt << 'EOF'
L'ATP, o adenosina trifosfato, è la principale fonte di energia cellulare.
La sua sintesi avviene attraverso la fosforilazione ossidativa nelle mitocondrie.
Il processo coinvolge NADH, FADH2 e il complesso della ATP sintasi.
EOF

# Con preprocessing biochimica
python src/generate_cloned_audio.py \
  -i INPUT/lezione_atp.txt \
  -c config/clone_professore.json \
  --use-biochem-preprocessor

# Preview preprocessing prima di generare
python src/generate_cloned_audio.py \
  -i INPUT/lezione_atp.txt \
  -c config/clone_professore.json \
  --preview-preprocessing
```

### Gestione Voci Multiple

```bash
# Scenario: Podcast con 2 speaker
# Speaker 1 (host)
python src/extract_audio_from_video.py \
  -i host_video.mp4 \
  -o VOICE_SAMPLES/host.wav \
  --start 5 --duration 5

# Speaker 2 (guest)
python src/extract_audio_from_video.py \
  -i guest_video.mp4 \
  -o VOICE_SAMPLES/guest.wav \
  --start 10 --duration 6

# Crea config per entrambi
cat > config/clone_host.json << 'EOF'
{
  "mode": "voice_clone",
  "language": "Italian",
  "prompt_speech_path": "VOICE_SAMPLES/host.wav",
  "output_format": "wav"
}
EOF

cat > config/clone_guest.json << 'EOF'
{
  "mode": "voice_clone",
  "language": "Italian",
  "prompt_speech_path": "VOICE_SAMPLES/guest.wav",
  "output_format": "wav"
}
EOF

# Genera dialogo
cat > INPUT/host_intro.txt << 'EOF'
Benvenuti al nostro podcast! Oggi abbiamo un ospite speciale.
EOF

cat > INPUT/guest_risposta.txt << 'EOF'
Grazie per l'invito! Sono felice di essere qui oggi.
EOF

python src/generate_cloned_audio.py -i INPUT/host_intro.txt -c config/clone_host.json -o OUTPUT/01_host_intro.wav
python src/generate_cloned_audio.py -i INPUT/guest_risposta.txt -c config/clone_guest.json -o OUTPUT/02_guest_risposta.wav
```

### Utility Script

```bash
# Lista tutti i campioni disponibili
python src/list_voice_samples.py

# Lista con dettagli
python src/list_voice_samples.py --details

# Prepara campione ottimale
python src/prepare_voice_sample.py \
  -i raw_audio.mp3 \
  -o VOICE_SAMPLES/optimized.wav

# Suggerisci miglior segmento
python src/prepare_voice_sample.py \
  -i long_audio.wav \
  --suggest
```

### Estrazione Batch da Video

```bash
# Estrai audio da tutti i video in una cartella
mkdir -p videos/
# (copia video MP4 in videos/)

python src/extract_audio_from_video.py \
  -i videos/ \
  -o VOICE_SAMPLES/extracted/

# Verifica risultati
python src/list_voice_samples.py
```

### Tips Voice Cloning

```bash
# 1. Trova segmento migliore nel video
# Apri video in player (QuickTime, VLC)
# Identifica segmento con voce chiara (5-7s)
# Annota timestamp (es. 01:23 = 83 secondi)

# 2. Estrai segmento ottimale
python src/extract_audio_from_video.py \
  -i video.mp4 \
  -o VOICE_SAMPLES/voice.wav \
  --start 83 \
  --duration 6

# 3. Verifica qualità
python src/list_voice_samples.py
# Cerca: ✓ = Ottimale, ⚠ = Accettabile, ✗ = Sconsigliato

# 4. Se necessario, ottimizza
python src/prepare_voice_sample.py \
  -i VOICE_SAMPLES/voice.wav \
  -o VOICE_SAMPLES/voice_clean.wav
```

### Confronto VoiceDesign vs VoiceClone

```bash
# Stesso testo con VoiceDesign
python src/generate_audio.py \
  -i INPUT/test.txt \
  -c config/voice_config.json \
  -o OUTPUT/voicedesign_test.wav

# Stesso testo con VoiceClone
python src/generate_cloned_audio.py \
  -i INPUT/test.txt \
  -c config/clone_config_speaker1.json \
  -o OUTPUT/voiceclone_test.wav

# Confronta risultati
open OUTPUT/voicedesign_test.wav
open OUTPUT/voiceclone_test.wav
```

---

**Voice Cloning avanzato?** Consulta [docs/VOICE_CLONING_GUIDE.md](docs/VOICE_CLONING_GUIDE.md)

**Altri esempi?** Vedi [README.md](README.md) per documentazione completa!
