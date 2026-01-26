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

---

**Hai bisogno di altri esempi?** Consulta [README.md](README.md) per documentazione completa!
