#!/usr/bin/env python3
"""
Script utility per preparare campioni vocali ottimali per voice cloning.
Normalizza audio, converte formato, rimuove silenzio, e verifica qualità.
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path


def check_ffmpeg():
    """Verifica che ffmpeg sia installato."""
    try:
        result = subprocess.run(
            ['ffmpeg', '-version'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=5
        )
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def get_audio_duration(audio_file):
    """Ottiene durata file audio."""
    try:
        cmd = [
            'ffprobe',
            '-i', str(audio_file),
            '-show_entries', 'format=duration',
            '-v', 'quiet',
            '-of', 'csv=p=0'
        ]
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=10)
        if result.returncode == 0:
            return float(result.stdout.decode('utf-8').strip())
    except:
        pass
    return None


def prepare_voice_sample(
    input_file,
    output_file,
    target_duration=None,
    start_time=0,
    remove_silence=True,
    normalize=True,
    target_sr=24000
):
    """
    Prepara campione vocale ottimale per voice cloning.

    Args:
        input_file: File audio input
        output_file: File audio output (.wav)
        target_duration: Durata target in secondi (None = mantieni originale)
        start_time: Timestamp inizio in secondi
        remove_silence: Se True, rimuove silenzio iniziale/finale
        normalize: Se True, normalizza volume
        target_sr: Sample rate target (default 24000 Hz)

    Returns:
        True se successo, False altrimenti
    """
    if not os.path.exists(input_file):
        print(f"✗ Errore: File non trovato: {input_file}")
        return False

    print(f"🔧 Preparazione campione vocale...")
    print(f"   Input: {Path(input_file).name}")

    # Analizza durata originale
    original_duration = get_audio_duration(input_file)
    if original_duration:
        print(f"   Durata originale: {original_duration:.2f}s")

    # Costruisci filtri audio
    filters = []

    # Rimozione silenzio
    if remove_silence:
        # Rimuove silenzio iniziale e finale
        filters.append("silenceremove=start_periods=1:start_duration=0.1:start_threshold=-50dB:"
                      "stop_periods=1:stop_duration=0.2:stop_threshold=-50dB")

    # Normalizzazione volume
    if normalize:
        filters.append("loudnorm=I=-16:TP=-1.5:LRA=11")

    # Costruisci comando ffmpeg
    cmd = ['ffmpeg', '-i', input_file]

    # Start time se specificato
    if start_time > 0:
        cmd.extend(['-ss', str(start_time)])

    # Durata target se specificata
    if target_duration:
        cmd.extend(['-t', str(target_duration)])

    # Applica filtri
    if filters:
        filter_complex = ','.join(filters)
        cmd.extend(['-af', filter_complex])

    # Parametri output
    cmd.extend([
        '-ar', str(target_sr),  # Sample rate
        '-ac', '1',  # Mono
        '-acodec', 'pcm_s16le',  # WAV codec
        '-y',  # Sovrascrivi
        output_file
    ])

    try:
        print(f"   Conversione in corso...")
        if remove_silence:
            print(f"   - Rimozione silenzio: ATTIVO")
        if normalize:
            print(f"   - Normalizzazione: ATTIVO")
        print(f"   - Sample rate: {target_sr} Hz")
        print(f"   - Canali: mono")

        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=120
        )

        if result.returncode == 0 and os.path.exists(output_file):
            # Verifica durata output
            output_duration = get_audio_duration(output_file)
            file_size = os.path.getsize(output_file) / (1024 * 1024)

            print(f"\n✓ Campione preparato con successo!")
            print(f"   Output: {output_file}")
            if output_duration:
                print(f"   Durata finale: {output_duration:.2f}s")

                # Valuta qualità
                if 3 <= output_duration <= 10:
                    print(f"   ✓ Durata ottimale per voice cloning (3-10s)")
                elif output_duration < 3:
                    print(f"   ⚠ ATTENZIONE: Durata < 3s. Raccomandato 3-10s")
                else:
                    print(f"   ⚠ Durata > 10s. Considera di ritagliare ulteriormente")

            print(f"   Size: {file_size:.2f} MB")
            return True
        else:
            print(f"✗ Errore durante conversione:")
            print(result.stderr.decode('utf-8', errors='ignore'))
            return False

    except subprocess.TimeoutExpired:
        print("✗ Errore: Timeout durante conversione (>120s)")
        return False
    except Exception as e:
        print(f"✗ Errore: {e}")
        return False


def suggest_best_segment(audio_file, target_duration=5):
    """
    Suggerisce il miglior segmento di durata target_duration.

    Returns:
        Tuple (start_time, duration) o None
    """
    # Per ora implementazione semplice: suggerisce di partire dall'inizio
    # In futuro si potrebbe analizzare il volume per trovare il segmento migliore

    total_duration = get_audio_duration(audio_file)
    if not total_duration:
        return None

    if total_duration <= target_duration:
        return (0, total_duration)

    # Suggerisci di partire dopo 1 secondo (evita fade-in iniziale)
    start = 1.0
    duration = min(target_duration, total_duration - start)

    return (start, duration)


def main():
    parser = argparse.ArgumentParser(
        description='Prepara campioni vocali ottimali per voice cloning',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Esempi:
  # Prepara campione con impostazioni ottimali
  python prepare_voice_sample.py -i input.mp3 -o VOICE_SAMPLES/speaker.wav

  # Estrai 5 secondi partendo dal secondo 10
  python prepare_voice_sample.py -i input.wav -o output.wav --start 10 --duration 5

  # Senza normalizzazione
  python prepare_voice_sample.py -i input.wav -o output.wav --no-normalize

  # Suggerisci miglior segmento
  python prepare_voice_sample.py -i input.mp3 --suggest
        """
    )

    parser.add_argument(
        '-i', '--input',
        required=True,
        help='File audio input'
    )

    parser.add_argument(
        '-o', '--output',
        help='File audio output (.wav). Richiesto se non usi --suggest'
    )

    parser.add_argument(
        '--start',
        type=float,
        default=0,
        help='Timestamp inizio in secondi (default: 0)'
    )

    parser.add_argument(
        '--duration',
        type=float,
        help='Durata in secondi (default: mantieni originale)'
    )

    parser.add_argument(
        '--no-silence-removal',
        action='store_true',
        help='Non rimuovere silenzio iniziale/finale'
    )

    parser.add_argument(
        '--no-normalize',
        action='store_true',
        help='Non normalizzare volume'
    )

    parser.add_argument(
        '--sample-rate',
        type=int,
        default=24000,
        help='Sample rate target in Hz (default: 24000)'
    )

    parser.add_argument(
        '--suggest',
        action='store_true',
        help='Suggerisci miglior segmento senza convertire'
    )

    args = parser.parse_args()

    # Verifica ffmpeg
    if not check_ffmpeg():
        print("✗ Errore: ffmpeg non trovato")
        print("\nInstallare ffmpeg:")
        print("  macOS: brew install ffmpeg")
        print("  Ubuntu: sudo apt install ffmpeg")
        sys.exit(1)

    # Modalità suggerimento
    if args.suggest:
        print(f"📊 Analisi file: {args.input}")
        suggestion = suggest_best_segment(args.input)
        if suggestion:
            start, duration = suggestion
            print(f"\n💡 Suggerimento miglior segmento:")
            print(f"   Start: {start:.1f}s")
            print(f"   Duration: {duration:.1f}s")
            print(f"\nComando suggerito:")
            print(f"   python prepare_voice_sample.py -i {args.input} -o VOICE_SAMPLES/sample.wav "
                  f"--start {start:.1f} --duration {duration:.1f}")
        else:
            print("✗ Impossibile analizzare file")
        sys.exit(0)

    # Verifica output specificato
    if not args.output:
        print("✗ Errore: --output richiesto (o usa --suggest per suggerimenti)")
        sys.exit(1)

    # Crea directory output se necessario
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)

    # Prepara campione
    success = prepare_voice_sample(
        input_file=args.input,
        output_file=args.output,
        target_duration=args.duration,
        start_time=args.start,
        remove_silence=not args.no_silence_removal,
        normalize=not args.no_normalize,
        target_sr=args.sample_rate
    )

    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
