#!/usr/bin/env python3
"""
Script di test rapido per verificare l'installazione di Qwen3-TTS.
Esegue controlli su tutte le dipendenze e configurazione.
"""

import sys


def test_imports():
    """Testa import di tutti i moduli richiesti."""
    print("🧪 Test 1: Verifica moduli Python")
    print("─" * 50)

    modules_status = {}

    # PyTorch
    try:
        import torch
        modules_status['torch'] = True
        print(f"✓ PyTorch {torch.__version__}")
        print(f"  - CUDA disponibile: {torch.cuda.is_available()}")
        print(f"  - MPS disponibile: {torch.backends.mps.is_available()}")
        if torch.backends.mps.is_available():
            print(f"  - MPS built: {torch.backends.mps.is_built()}")
    except ImportError as e:
        modules_status['torch'] = False
        print(f"❌ PyTorch: {e}")

    # soundfile
    try:
        import soundfile as sf
        modules_status['soundfile'] = True
        print(f"✓ soundfile {sf.__version__}")
    except ImportError as e:
        modules_status['soundfile'] = False
        print(f"❌ soundfile: {e}")

    # pydub (opzionale)
    try:
        import pydub
        modules_status['pydub'] = True
        print(f"✓ pydub installato")
    except ImportError:
        modules_status['pydub'] = False
        print(f"⚠ pydub non installato (opzionale, per MP3)")
    except AttributeError:
        modules_status['pydub'] = True
        print(f"✓ pydub installato")

    # qwen-tts
    try:
        from qwen_tts import Qwen3TTSModel
        modules_status['qwen_tts'] = True
        print(f"✓ qwen-tts installato")
    except ImportError as e:
        modules_status['qwen_tts'] = False
        print(f"❌ qwen-tts: {e}")

    # tqdm
    try:
        import tqdm
        modules_status['tqdm'] = True
        print(f"✓ tqdm {tqdm.__version__}")
    except ImportError:
        modules_status['tqdm'] = False
        print(f"❌ tqdm non installato")

    return modules_status


def test_flash_attention():
    """Testa disponibilità Flash Attention 2."""
    print("\n🧪 Test 2: Flash Attention 2")
    print("─" * 50)

    try:
        import flash_attn
        print(f"✓ Flash Attention 2 installato")
        print(f"  Versione: {flash_attn.__version__}")
        return True
    except ImportError:
        print(f"⚠ Flash Attention 2 non installato (opzionale)")
        print(f"  Installare con: MAX_JOBS=4 pip install -U flash-attn --no-build-isolation")
        return False


def test_ffmpeg():
    """Testa disponibilità ffmpeg."""
    print("\n🧪 Test 3: ffmpeg")
    print("─" * 50)

    import subprocess
    try:
        result = subprocess.run(
            ['ffmpeg', '-version'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            version_line = result.stdout.split('\n')[0]
            print(f"✓ ffmpeg trovato")
            print(f"  {version_line}")
            return True
        else:
            print(f"❌ ffmpeg non funziona correttamente")
            return False
    except FileNotFoundError:
        print(f"⚠ ffmpeg non trovato (opzionale, per MP3)")
        print(f"  Installare con: brew install ffmpeg")
        return False
    except Exception as e:
        print(f"⚠ Errore verifica ffmpeg: {e}")
        return False


def test_file_structure():
    """Verifica struttura directory del progetto."""
    print("\n🧪 Test 4: Struttura progetto")
    print("─" * 50)

    import os
    from pathlib import Path

    required_dirs = ['INPUT', 'OUTPUT', 'config', 'src', 'models']
    required_files = [
        'config/voice_config.json',
        'src/generate_audio.py',
        'src/batch_process.py',
    ]

    all_ok = True

    for dir_name in required_dirs:
        if os.path.isdir(dir_name):
            print(f"✓ Directory {dir_name}/ presente")
        else:
            print(f"❌ Directory {dir_name}/ mancante")
            all_ok = False

    for file_path in required_files:
        if os.path.isfile(file_path):
            print(f"✓ File {file_path} presente")
        else:
            print(f"❌ File {file_path} mancante")
            all_ok = False

    return all_ok


def test_config_files():
    """Verifica validità file di configurazione."""
    print("\n🧪 Test 5: File di configurazione")
    print("─" * 50)

    import json
    from pathlib import Path

    config_files = list(Path('config').glob('*.json'))
    all_ok = True

    for config_file in config_files:
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)

            # Verifica campi richiesti
            required_fields = ['language', 'voice_description', 'output_format']
            missing = [f for f in required_fields if f not in config]

            if missing:
                print(f"⚠ {config_file.name}: campi mancanti: {missing}")
                all_ok = False
            else:
                print(f"✓ {config_file.name}: valido")
                print(f"  - Lingua: {config['language']}")
                print(f"  - Formato: {config['output_format']}")

        except json.JSONDecodeError as e:
            print(f"❌ {config_file.name}: JSON non valido: {e}")
            all_ok = False
        except Exception as e:
            print(f"❌ {config_file.name}: errore: {e}")
            all_ok = False

    return all_ok


def print_summary(results):
    """Stampa riepilogo risultati."""
    print("\n" + "═" * 50)
    print("📊 RIEPILOGO TEST")
    print("═" * 50)

    all_critical_ok = all([
        results['modules']['torch'],
        results['modules']['soundfile'],
        results['modules']['qwen_tts'],
        results['file_structure'],
        results['config_files']
    ])

    if all_critical_ok:
        print("✅ Sistema pronto all'uso!")
        print("\n📝 Prossimi passi:")
        print("1. conda activate qwen3-tts")
        print("2. python src/generate_audio.py -i INPUT/esempio.txt")
    else:
        print("❌ Alcuni componenti critici mancanti")
        print("\n🔧 Azioni richieste:")

        if not results['modules']['torch']:
            print("- Installare PyTorch: pip install torch")
        if not results['modules']['soundfile']:
            print("- Installare soundfile: pip install soundfile")
        if not results['modules']['qwen_tts']:
            print("- Installare qwen-tts: pip install qwen-tts")
        if not results['file_structure']:
            print("- Verificare struttura directory del progetto")
        if not results['config_files']:
            print("- Verificare file di configurazione in config/")

    print("\n⚠ Componenti opzionali:")
    if not results['modules'].get('pydub', False):
        print("- pydub (per MP3): pip install pydub")
    if not results['flash_attention']:
        print("- Flash Attention 2: MAX_JOBS=4 pip install -U flash-attn --no-build-isolation")
    if not results['ffmpeg']:
        print("- ffmpeg (per MP3): brew install ffmpeg")

    print("═" * 50)

    return all_critical_ok


def main():
    print("╔════════════════════════════════════════════════╗")
    print("║     Test Installazione Qwen3-TTS (M3 Max)     ║")
    print("╚════════════════════════════════════════════════╝")
    print()

    results = {
        'modules': test_imports(),
        'flash_attention': test_flash_attention(),
        'ffmpeg': test_ffmpeg(),
        'file_structure': test_file_structure(),
        'config_files': test_config_files(),
    }

    success = print_summary(results)
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
