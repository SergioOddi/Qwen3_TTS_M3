#!/bin/bash
# Script di setup per ambiente TTS_M3 su MacBook Pro M3 Max

set -e  # Exit on error

echo "🚀 Setup ambiente Qwen3-TTS per M3 Max"
echo "======================================"

# Verifica sistema operativo
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo "⚠️  Warning: Questo script è ottimizzato per macOS (M3 Max)"
fi

# Verifica conda
if ! command -v conda &> /dev/null; then
    echo "❌ Errore: conda non trovato"
    echo "   Installare Miniconda o Anaconda: https://docs.conda.io/en/latest/miniconda.html"
    exit 1
fi

echo ""
echo "📦 Step 1: Creazione ambiente conda"
echo "-----------------------------------"
read -p "Nome ambiente (default: qwen3-tts): " ENV_NAME
ENV_NAME=${ENV_NAME:-qwen3-tts}

# Verifica se ambiente esiste già
if conda env list | grep -q "^$ENV_NAME "; then
    echo "⚠️  L'ambiente '$ENV_NAME' esiste già"
    read -p "Rimuovere e ricreare? (s/N): " RECREATE
    if [[ $RECREATE =~ ^[Ss]$ ]]; then
        echo "🗑️  Rimozione ambiente esistente..."
        conda env remove -n $ENV_NAME -y
    else
        echo "ℹ️  Uso ambiente esistente"
    fi
fi

# Crea o attiva ambiente
if ! conda env list | grep -q "^$ENV_NAME "; then
    echo "✨ Creazione nuovo ambiente Python 3.12..."
    conda create -n $ENV_NAME python=3.12 -y
fi

echo ""
echo "📚 Step 2: Installazione dipendenze Python"
echo "------------------------------------------"
# Nota: source conda potrebbe non funzionare in script, usa eval
eval "$(conda shell.bash hook)"
conda activate $ENV_NAME

# Verifica attivazione
if [[ "$CONDA_DEFAULT_ENV" != "$ENV_NAME" ]]; then
    echo "❌ Errore: impossibile attivare ambiente conda"
    echo "   Prova manualmente: conda activate $ENV_NAME"
    exit 1
fi

echo "✓ Ambiente '$ENV_NAME' attivo"

# Installa dipendenze base
echo ""
echo "📥 Installazione dipendenze da requirements.txt..."
pip install -r requirements.txt

echo ""
echo "⚡ Step 3: Flash Attention 2 (opzionale)"
echo "----------------------------------------"
read -p "Installare Flash Attention 2 per migliori performance? (s/N): " INSTALL_FA
if [[ $INSTALL_FA =~ ^[Ss]$ ]]; then
    echo "🔧 Installazione Flash Attention 2..."
    echo "   Questo può richiedere diversi minuti..."
    MAX_JOBS=4 pip install -U flash-attn --no-build-isolation || {
        echo "⚠️  Installazione Flash Attention 2 fallita"
        echo "   Il sistema continuerà a funzionare con implementazione standard"
    }
else
    echo "⏭️  Saltato Flash Attention 2"
fi

echo ""
echo "🎵 Step 4: Verifica ffmpeg (per conversione MP3)"
echo "------------------------------------------------"
if command -v ffmpeg &> /dev/null; then
    echo "✓ ffmpeg trovato: $(ffmpeg -version | head -n1)"
else
    echo "⚠️  ffmpeg non trovato"
    read -p "Installare ffmpeg con Homebrew? (s/N): " INSTALL_FFMPEG
    if [[ $INSTALL_FFMPEG =~ ^[Ss]$ ]]; then
        if command -v brew &> /dev/null; then
            brew install ffmpeg
        else
            echo "❌ Homebrew non trovato"
            echo "   Installare manualmente ffmpeg da: https://ffmpeg.org/"
        fi
    else
        echo "ℹ️  Conversione MP3 non sarà disponibile"
        echo "   Installare in seguito con: brew install ffmpeg"
    fi
fi

echo ""
echo "🧪 Step 5: Test installazione"
echo "-----------------------------"
echo "Verifica import moduli..."

python -c "
import sys
try:
    import torch
    print('✓ PyTorch:', torch.__version__)
    print('  - MPS disponibile:', torch.backends.mps.is_available())

    import soundfile
    print('✓ soundfile:', soundfile.__version__)

    try:
        import pydub
        print('✓ pydub:', pydub.__version__)
    except ImportError:
        print('⚠ pydub non installato')

    try:
        from qwen_tts import Qwen3TTSModel
        print('✓ qwen-tts installato correttamente')
    except ImportError as e:
        print('❌ Errore import qwen-tts:', e)
        sys.exit(1)

    print('\n✅ Tutti i moduli core installati correttamente!')

except Exception as e:
    print(f'❌ Errore durante verifica: {e}')
    sys.exit(1)
"

if [ $? -eq 0 ]; then
    echo ""
    echo "╔════════════════════════════════════════════════╗"
    echo "║  ✅ Setup completato con successo!            ║"
    echo "╚════════════════════════════════════════════════╝"
    echo ""
    echo "📝 Prossimi passi:"
    echo ""
    echo "1. Attiva l'ambiente:"
    echo "   conda activate $ENV_NAME"
    echo ""
    echo "2. Crea un file di testo in INPUT/"
    echo "   echo 'Ciao, questo è un test.' > INPUT/test.txt"
    echo ""
    echo "3. Genera audio:"
    echo "   python src/generate_audio.py -i INPUT/test.txt"
    echo ""
    echo "4. Per elaborazione batch:"
    echo "   python src/batch_process.py"
    echo ""
    echo "📚 Leggi README.md per maggiori informazioni"
else
    echo ""
    echo "❌ Setup completato con errori"
    echo "   Verifica i messaggi di errore sopra"
    exit 1
fi
