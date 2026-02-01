#!/usr/bin/env python3
"""
Script utility per listare tutti i campioni vocali disponibili in VOICE_SAMPLES/.
Mostra informazioni dettagliate su ciascun file audio.
"""

import argparse
import os
import subprocess
from pathlib import Path


def get_audio_info(audio_file):
    """
    Ottiene informazioni dettagliate su file audio usando ffprobe.

    Returns:
        Dict con: duration, sample_rate, channels, codec, bitrate
    """
    info = {
        'duration': None,
        'sample_rate': None,
        'channels': None,
        'codec': None,
        'bitrate': None
    }

    try:
        # Durata
        cmd = [
            'ffprobe',
            '-i', str(audio_file),
            '-show_entries', 'format=duration',
            '-v', 'quiet',
            '-of', 'csv=p=0'
        ]
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=10)
        if result.returncode == 0:
            info['duration'] = float(result.stdout.decode('utf-8').strip())

        # Sample rate, channels, codec
        cmd = [
            'ffprobe',
            '-i', str(audio_file),
            '-show_entries', 'stream=sample_rate,channels,codec_name',
            '-select_streams', 'a:0',
            '-v', 'quiet',
            '-of', 'csv=p=0'
        ]
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=10)
        if result.returncode == 0:
            parts = result.stdout.decode('utf-8').strip().split(',')
            if len(parts) >= 2:
                info['codec'] = parts[0]
                info['sample_rate'] = int(parts[1]) if parts[1].isdigit() else None
                info['channels'] = int(parts[2]) if len(parts) > 2 and parts[2].isdigit() else None

    except Exception:
        pass

    return info


def format_duration(seconds):
    """Formatta durata in formato leggibile."""
    if seconds is None:
        return "N/A"
    if seconds < 60:
        return f"{seconds:.1f}s"
    else:
        mins = int(seconds // 60)
        secs = seconds % 60
        return f"{mins}m {secs:.1f}s"


def format_channels(channels):
    """Formatta numero canali."""
    if channels is None:
        return "N/A"
    elif channels == 1:
        return "mono"
    elif channels == 2:
        return "stereo"
    else:
        return f"{channels}ch"


def format_sample_rate(sr):
    """Formatta sample rate."""
    if sr is None:
        return "N/A"
    return f"{sr/1000:.1f}kHz" if sr >= 1000 else f"{sr}Hz"


def get_quality_indicator(info):
    """
    Ritorna indicatore qualità per voice cloning.

    Returns:
        str: "✓" (ottimale), "⚠" (accettabile), "✗" (sconsigliato)
    """
    duration = info.get('duration')
    sample_rate = info.get('sample_rate')
    channels = info.get('channels')

    if duration is None:
        return "?"

    # Durata ottimale: 3-10 secondi
    if duration < 3:
        return "✗"  # Troppo corto
    elif duration > 10:
        return "⚠"  # Troppo lungo
    else:
        # Verifica anche sample rate e canali
        if sample_rate and sample_rate >= 16000 and channels == 1:
            return "✓"  # Ottimale
        else:
            return "⚠"  # Accettabile ma non ottimale

    return "⚠"


def list_voice_samples(voice_samples_dir, show_details=False):
    """Lista tutti i campioni vocali nella directory."""
    samples_path = Path(voice_samples_dir)

    if not samples_path.exists():
        print(f"✗ Directory non trovata: {voice_samples_dir}")
        return

    # Estensioni audio supportate
    audio_extensions = ['.wav', '.mp3', '.flac', '.ogg', '.m4a']
    audio_files = []

    for ext in audio_extensions:
        audio_files.extend(samples_path.glob(f"*{ext}"))
        audio_files.extend(samples_path.glob(f"*{ext.upper()}"))

    # Includi anche file in extracted/
    extracted_path = samples_path / "extracted"
    if extracted_path.exists():
        for ext in audio_extensions:
            audio_files.extend(extracted_path.glob(f"*{ext}"))

    # Rimuovi .gitkeep
    audio_files = [f for f in audio_files if f.name != '.gitkeep']
    audio_files = sorted(set(audio_files))

    if not audio_files:
        print(f"⚠ Nessun campione audio trovato in {voice_samples_dir}")
        print("\n💡 Suggerimenti:")
        print("   1. Estrai audio da video MP4 con: python src/extract_audio_from_video.py")
        print("   2. Copia file audio .wav/.mp3 in VOICE_SAMPLES/")
        return

    print(f"\n{'='*70}")
    print(f"🎤 CAMPIONI VOCALI DISPONIBILI ({len(audio_files)} file)")
    print(f"{'='*70}\n")

    for i, audio_file in enumerate(audio_files, 1):
        info = get_audio_info(audio_file)
        quality = get_quality_indicator(info)

        # Path relativo
        rel_path = audio_file.relative_to(samples_path.parent)

        # Dimensione file
        file_size = audio_file.stat().st_size / (1024 * 1024)  # MB

        print(f"{i}. {quality} {audio_file.name}")
        print(f"   Path: {rel_path}")
        print(f"   Durata: {format_duration(info['duration'])} | "
              f"Sample rate: {format_sample_rate(info['sample_rate'])} | "
              f"Canali: {format_channels(info['channels'])} | "
              f"Size: {file_size:.2f} MB")

        if show_details and info['codec']:
            print(f"   Codec: {info['codec']}")

        # Suggerimenti basati su qualità
        if quality == "✗":
            print(f"   ⚠ ATTENZIONE: Durata < 3s. Raccomandato 3-10s per voice cloning")
        elif quality == "⚠":
            if info['duration'] and info['duration'] > 10:
                print(f"   💡 Suggerimento: Durata > 10s. Considera di ritagliare a 5-8s")
            if info['channels'] and info['channels'] > 1:
                print(f"   💡 Suggerimento: Audio stereo. Mono è preferibile per cloning")
            if info['sample_rate'] and info['sample_rate'] < 16000:
                print(f"   💡 Suggerimento: Sample rate basso. Raccomandato >= 16kHz")

        print()

    # Legenda
    print(f"{'─'*70}")
    print("Legenda qualità:")
    print("  ✓ = Ottimale per voice cloning (3-10s, mono, >= 16kHz)")
    print("  ⚠ = Accettabile ma non ottimale")
    print("  ✗ = Sconsigliato (troppo corto)")
    print(f"{'='*70}\n")


def main():
    parser = argparse.ArgumentParser(
        description='Lista campioni vocali disponibili per voice cloning',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Esempi:
  # Lista tutti i campioni in VOICE_SAMPLES/
  python list_voice_samples.py

  # Mostra dettagli aggiuntivi
  python list_voice_samples.py --details

  # Specifica directory custom
  python list_voice_samples.py -d MY_SAMPLES/
        """
    )

    parser.add_argument(
        '--dir', '-d',
        default='VOICE_SAMPLES',
        help='Directory contenente campioni vocali (default: VOICE_SAMPLES)'
    )

    parser.add_argument(
        '--details',
        action='store_true',
        help='Mostra informazioni dettagliate (codec, etc.)'
    )

    args = parser.parse_args()

    list_voice_samples(args.dir, show_details=args.details)


if __name__ == '__main__':
    main()
