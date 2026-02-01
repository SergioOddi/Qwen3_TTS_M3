#!/usr/bin/env python3
"""
Script per elaborazione batch di file di testo con voice cloning.
Processa tutti i file .txt nella directory INPUT/ usando lo stesso campione vocale.
"""

import argparse
import os
import sys
from pathlib import Path
from datetime import datetime

import torch
from qwen_tts import Qwen3TTSModel
from tqdm import tqdm

from generate_cloned_audio import generate_cloned_audio, load_config


def find_text_files(input_dir):
    """Trova tutti i file .txt nella directory input."""
    input_path = Path(input_dir)
    if not input_path.exists():
        return []

    txt_files = list(input_path.glob('*.txt'))
    # Rimuovi .gitkeep se presente
    txt_files = [f for f in txt_files if f.name != '.gitkeep']
    return sorted(txt_files)


def batch_clone_process(
    input_dir,
    output_dir,
    config_path,
    skip_existing=True,
    use_biochem_preprocessor=False
):
    """
    Processa tutti i file di testo in batch con voice cloning.

    Args:
        input_dir: Directory contenente file .txt
        output_dir: Directory per output audio
        config_path: Path al file di configurazione voice cloning
        skip_existing: Se True, salta file già processati
        use_biochem_preprocessor: Se True, applica preprocessing biochimica

    Returns:
        Dict con statistiche di elaborazione
    """
    # Trova file da processare
    text_files = find_text_files(input_dir)

    if not text_files:
        print(f"⚠ Nessun file .txt trovato in {input_dir}")
        return {'total': 0, 'success': 0, 'skipped': 0, 'failed': 0}

    print(f"📚 Trovati {len(text_files)} file da processare")

    # Carica configurazione
    config = load_config(config_path)
    output_format = config.get('output_format', 'wav')
    prompt_speech_path = config.get('prompt_speech_path')

    # Verifica campione audio
    if not prompt_speech_path:
        print("❌ Errore: 'prompt_speech_path' non specificato nella configurazione")
        return {'total': len(text_files), 'success': 0, 'skipped': 0, 'failed': len(text_files)}

    if not os.path.exists(prompt_speech_path):
        print(f"❌ Errore: Campione audio non trovato: {prompt_speech_path}")
        return {'total': len(text_files), 'success': 0, 'skipped': 0, 'failed': len(text_files)}

    print(f"🎤 Campione vocale: {prompt_speech_path}")
    if use_biochem_preprocessor:
        print("🔬 Preprocessing biochimica: ATTIVO")

    # Carica modello una sola volta
    print("🔄 Caricamento modello Qwen3-TTS Base (voice cloning)...")
    try:
        model = Qwen3TTSModel.from_pretrained(
            "Qwen/Qwen3-TTS-12Hz-1.7B-Base",
            device_map="mps",
            dtype=torch.bfloat16,
            attn_implementation="flash_attention_2",
        )
        print("✓ Modello caricato con successo (con Flash Attention 2)")
    except Exception as e:
        print("⚠ Flash Attention 2 non disponibile, uso implementazione standard")
        try:
            model = Qwen3TTSModel.from_pretrained(
                "Qwen/Qwen3-TTS-12Hz-1.7B-Base",
                device_map="mps",
                dtype=torch.bfloat16,
            )
            print("✓ Modello caricato con successo")
        except Exception as e2:
            print(f"❌ Errore caricamento modello: {e2}")
            return {'total': len(text_files), 'success': 0, 'skipped': 0, 'failed': len(text_files)}

    # Statistiche
    stats = {
        'total': len(text_files),
        'success': 0,
        'skipped': 0,
        'failed': 0,
        'start_time': datetime.now()
    }

    # Processa file
    print(f"\n🎵 Inizio elaborazione batch (voice cloning)...")
    print(f"{'='*60}")

    for text_file in tqdm(text_files, desc="Elaborazione"):
        output_file = Path(output_dir) / f"{text_file.stem}_cloned.{output_format}"

        # Salta se esiste già
        if skip_existing and output_file.exists():
            print(f"\n⏭️  Saltato (già esistente): {text_file.name}")
            stats['skipped'] += 1
            continue

        print(f"\n📄 Elaborazione: {text_file.name}")
        print(f"   Output: {output_file}")

        # Genera audio con voice cloning
        result = generate_cloned_audio(
            input_file=str(text_file),
            output_file=str(output_file),
            config_path=config_path,
            model=model,  # Riusa modello già caricato
            use_biochem_preprocessor=use_biochem_preprocessor
        )

        if result:
            stats['success'] += 1
        else:
            stats['failed'] += 1

        print(f"{'─'*60}")

    # Calcola tempo totale
    stats['end_time'] = datetime.now()
    stats['duration'] = stats['end_time'] - stats['start_time']

    return stats


def print_summary(stats):
    """Stampa riepilogo elaborazione."""
    print(f"\n{'='*60}")
    print("📊 RIEPILOGO ELABORAZIONE BATCH (VOICE CLONING)")
    print(f"{'='*60}")
    print(f"Totale file:      {stats['total']}")
    print(f"✅ Successo:      {stats['success']}")
    print(f"⏭️  Saltati:       {stats['skipped']}")
    print(f"❌ Falliti:       {stats['failed']}")
    print(f"⏱️  Tempo totale:  {stats['duration']}")
    print(f"{'='*60}")

    if stats['success'] > 0:
        avg_time = stats['duration'] / stats['success']
        print(f"⌚ Tempo medio per file: {avg_time}")


def main():
    parser = argparse.ArgumentParser(
        description='Elaborazione batch con voice cloning',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Esempi:
  # Batch processing base
  python batch_clone_process.py -c config/clone_config_speaker1.json

  # Specifica directory input/output custom
  python batch_clone_process.py -i MY_TEXTS/ -o MY_OUTPUT/ -c config/clone_config_speaker1.json

  # Rigenera anche file esistenti
  python batch_clone_process.py -c config/clone_config_speaker1.json --force

  # Con preprocessing biochimica
  python batch_clone_process.py -c config/clone_config_speaker1.json --use-biochem-preprocessor
        """
    )

    parser.add_argument(
        '--input', '-i',
        default='INPUT',
        help='Directory contenente file .txt (default: INPUT)'
    )

    parser.add_argument(
        '--output', '-o',
        default='OUTPUT',
        help='Directory per file audio (default: OUTPUT)'
    )

    parser.add_argument(
        '--config', '-c',
        required=True,
        help='Path al file di configurazione voice cloning (es. config/clone_config_speaker1.json)'
    )

    parser.add_argument(
        '--force', '-f',
        action='store_true',
        help='Rigenera anche file già esistenti'
    )

    parser.add_argument(
        '--use-biochem-preprocessor',
        action='store_true',
        help='Applica preprocessing per terminologia scientifica/biochimica'
    )

    args = parser.parse_args()

    # Verifica directory input esista
    if not os.path.exists(args.input):
        print(f"❌ Errore: directory input non trovata: {args.input}")
        sys.exit(1)

    # Verifica file config esista
    if not os.path.exists(args.config):
        print(f"❌ Errore: file configurazione non trovato: {args.config}")
        print(f"💡 Crea un file di configurazione voice cloning in: {args.config}")
        sys.exit(1)

    # Crea directory output se non esiste
    os.makedirs(args.output, exist_ok=True)

    # Elabora batch
    stats = batch_clone_process(
        input_dir=args.input,
        output_dir=args.output,
        config_path=args.config,
        skip_existing=not args.force,
        use_biochem_preprocessor=args.use_biochem_preprocessor
    )

    # Stampa riepilogo
    print_summary(stats)

    # Exit code basato su risultati
    if stats['failed'] > 0:
        sys.exit(1)
    elif stats['success'] == 0 and stats['skipped'] == 0:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == '__main__':
    main()
