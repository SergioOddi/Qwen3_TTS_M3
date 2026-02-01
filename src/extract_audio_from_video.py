#!/usr/bin/env python3
"""
Script per estrarre traccia audio da file MP4 per voice cloning.
Output: file WAV mono 24kHz ottimizzato per Qwen3-TTS.
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


def extract_audio(
    input_video,
    output_audio,
    start_time=None,
    duration=None,
    sample_rate=24000,
    channels=1
):
    """
    Estrae audio da file video usando ffmpeg.

    Args:
        input_video: Path file video input (.mp4, .mov, .avi, etc.)
        output_audio: Path file audio output (.wav)
        start_time: Timestamp inizio estrazione (es. "00:00:10" o 10)
        duration: Durata audio in secondi (es. 5 per 5 secondi)
        sample_rate: Frequenza campionamento (default 24000 Hz)
        channels: Numero canali (1=mono, 2=stereo)

    Returns:
        True se successo, False altrimenti
    """
    if not os.path.exists(input_video):
        print(f"✗ Errore: File video non trovato: {input_video}")
        return False

    # Costruisci comando ffmpeg
    cmd = ['ffmpeg', '-i', input_video]

    # Aggiungi parametri temporali se specificati
    if start_time is not None:
        # Converti in formato timestamp se necessario
        if isinstance(start_time, (int, float)):
            start_time = str(int(start_time))
        cmd.extend(['-ss', str(start_time)])

    if duration is not None:
        cmd.extend(['-t', str(duration)])

    # Parametri audio output
    cmd.extend([
        '-vn',  # No video
        '-acodec', 'pcm_s16le',  # Codec audio WAV
        '-ar', str(sample_rate),  # Sample rate
        '-ac', str(channels),  # Canali
        '-y',  # Sovrascrivi se esiste
        output_audio
    ])

    try:
        print(f"Estrazione audio da {Path(input_video).name}...")
        if start_time:
            print(f"  Start: {start_time}s", end='')
        if duration:
            print(f", Duration: {duration}s", end='')
        print()

        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=120
        )

        if result.returncode == 0 and os.path.exists(output_audio):
            file_size = os.path.getsize(output_audio) / (1024 * 1024)
            print(f"✓ Audio estratto: {output_audio} ({file_size:.2f} MB)")
            return True
        else:
            print(f"✗ Errore ffmpeg:")
            print(result.stderr.decode('utf-8', errors='ignore'))
            return False

    except subprocess.TimeoutExpired:
        print("✗ Errore: Timeout durante estrazione audio (>120s)")
        return False
    except Exception as e:
        print(f"✗ Errore durante estrazione: {e}")
        return False


def get_audio_duration(audio_file):
    """Ottiene durata file audio usando ffprobe."""
    try:
        cmd = [
            'ffprobe',
            '-i', audio_file,
            '-show_entries', 'format=duration',
            '-v', 'quiet',
            '-of', 'csv=p=0'
        ]
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=10
        )
        if result.returncode == 0:
            return float(result.stdout.decode('utf-8').strip())
    except:
        pass
    return None


def process_directory(input_dir, output_dir, **extract_params):
    """Processa tutti i video in una directory."""
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Estensioni video supportate
    video_extensions = ['.mp4', '.mov', '.avi', '.mkv', '.m4v', '.flv']
    video_files = []

    for ext in video_extensions:
        video_files.extend(input_path.glob(f"*{ext}"))
        video_files.extend(input_path.glob(f"*{ext.upper()}"))

    if not video_files:
        print(f"✗ Nessun file video trovato in {input_dir}")
        return

    print(f"Trovati {len(video_files)} file video da processare\n")

    success_count = 0
    for video_file in video_files:
        output_file = output_path / f"{video_file.stem}.wav"
        if extract_audio(str(video_file), str(output_file), **extract_params):
            success_count += 1
        print()  # Riga vuota tra file

    print(f"Completato: {success_count}/{len(video_files)} file estratti con successo")


def main():
    parser = argparse.ArgumentParser(
        description='Estrae audio da file video per voice cloning con Qwen3-TTS',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Esempi:
  # Estrai audio completo da video
  python extract_audio_from_video.py -i video.mp4 -o VOICE_SAMPLES/voice.wav

  # Estrai 5 secondi partendo dal secondo 10
  python extract_audio_from_video.py -i video.mp4 -o VOICE_SAMPLES/voice.wav --start 10 --duration 5

  # Processa tutti i video in una cartella
  python extract_audio_from_video.py -i videos/ -o VOICE_SAMPLES/extracted/
        """
    )

    parser.add_argument(
        '-i', '--input',
        required=True,
        help='File video input o cartella contenente video'
    )

    parser.add_argument(
        '-o', '--output',
        required=True,
        help='File audio output (.wav) o cartella output'
    )

    parser.add_argument(
        '--start',
        type=float,
        default=None,
        help='Timestamp inizio estrazione in secondi (es. 10 = inizia dal secondo 10)'
    )

    parser.add_argument(
        '--duration',
        type=float,
        default=None,
        help='Durata audio in secondi (es. 5 = estrae 5 secondi). Raccomandato 3-10s per voice cloning'
    )

    parser.add_argument(
        '--sample-rate',
        type=int,
        default=24000,
        help='Sample rate output in Hz (default: 24000, ottimale per Qwen3-TTS)'
    )

    parser.add_argument(
        '--stereo',
        action='store_true',
        help='Mantieni stereo (default: mono)'
    )

    args = parser.parse_args()

    # Verifica ffmpeg
    if not check_ffmpeg():
        print("✗ Errore: ffmpeg non trovato")
        print("\nInstallare ffmpeg:")
        print("  macOS: brew install ffmpeg")
        print("  Ubuntu: sudo apt install ffmpeg")
        print("  Windows: https://ffmpeg.org/download.html")
        sys.exit(1)

    channels = 2 if args.stereo else 1
    extract_params = {
        'start_time': args.start,
        'duration': args.duration,
        'sample_rate': args.sample_rate,
        'channels': channels
    }

    input_path = Path(args.input)
    output_path = Path(args.output)

    # Verifica se input è directory o file
    if input_path.is_dir():
        # Modalità batch
        process_directory(args.input, args.output, **extract_params)
    elif input_path.is_file():
        # Modalità singolo file
        # Crea directory output se necessario
        output_path.parent.mkdir(parents=True, exist_ok=True)

        success = extract_audio(
            args.input,
            args.output,
            **extract_params
        )

        if success:
            # Mostra info durata se disponibile
            duration = get_audio_duration(args.output)
            if duration:
                print(f"  Durata: {duration:.2f}s")
                if duration < 3:
                    print("\n⚠ Attenzione: Durata < 3s. Per voice cloning di qualità, raccomandati 3-10s")
                elif duration > 10:
                    print("\n⚠ Attenzione: Durata > 10s. Per voice cloning ottimale, raccomandati 3-10s")

            sys.exit(0)
        else:
            sys.exit(1)
    else:
        print(f"✗ Errore: Input non valido: {args.input}")
        print("  Specificare un file video o una cartella contenente video")
        sys.exit(1)


if __name__ == "__main__":
    main()
