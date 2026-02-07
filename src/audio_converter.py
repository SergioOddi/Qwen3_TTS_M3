#!/usr/bin/env python3
"""
Modulo per conversione formati audio (M4A, WAV, MP3).
Supporta conversioni bidirezionali tra formati usando pydub e ffmpeg.
"""

import os
import subprocess
from pathlib import Path
from typing import Optional, Tuple


def check_ffmpeg() -> bool:
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


class AudioConverter:
    """Classe per conversione formati audio."""

    SUPPORTED_FORMATS = {'m4a', 'wav', 'mp3'}
    DEFAULT_SAMPLE_RATE = 24000
    DEFAULT_BITRATE = '192k'
    MAX_TIMEOUT = 300  # 5 minuti

    def __init__(self, sample_rate: int = None, bitrate: str = None):
        """
        Inizializza converter.

        Args:
            sample_rate: Frequenza campionamento (default 24000 Hz)
            bitrate: Bitrate MP3 (default '192k')
        """
        self.sample_rate = sample_rate or self.DEFAULT_SAMPLE_RATE
        self.bitrate = bitrate or self.DEFAULT_BITRATE

        # Verifica ffmpeg
        if not check_ffmpeg():
            raise RuntimeError(
                "ffmpeg non trovato. Installare con: brew install ffmpeg"
            )

    def convert(
        self,
        input_path: str,
        output_path: str,
        input_format: str = None,
        output_format: str = None
    ) -> Tuple[bool, str]:
        """
        Converte file audio da un formato all'altro.

        Args:
            input_path: Path file input
            output_path: Path file output
            input_format: Formato input (auto-detect se None)
            output_format: Formato output (auto-detect se None)

        Returns:
            (success: bool, message: str)
        """
        # Validazione input
        if not os.path.exists(input_path):
            return False, f"File non trovato: {input_path}"

        # Auto-detect formati da estensioni
        if input_format is None:
            input_format = Path(input_path).suffix.lstrip('.').lower()
        if output_format is None:
            output_format = Path(output_path).suffix.lstrip('.').lower()

        # Validazione formati
        if input_format not in self.SUPPORTED_FORMATS:
            return False, f"Formato input non supportato: {input_format}"
        if output_format not in self.SUPPORTED_FORMATS:
            return False, f"Formato output non supportato: {output_format}"

        # Routing conversione
        conversion_key = f"{input_format}_to_{output_format}"
        conversion_map = {
            'm4a_to_wav': self._convert_m4a_to_wav,
            'm4a_to_mp3': self._convert_m4a_to_mp3,
            'wav_to_mp3': self._convert_wav_to_mp3,
            'wav_to_wav': self._convert_wav_to_wav,
            'mp3_to_wav': self._convert_mp3_to_wav,
            'mp3_to_mp3': self._convert_mp3_to_mp3,
        }

        converter_func = conversion_map.get(conversion_key)
        if converter_func is None:
            return False, f"Conversione {input_format}→{output_format} non supportata"

        # Esegui conversione
        return converter_func(input_path, output_path)

    def _convert_m4a_to_wav(self, input_path: str, output_path: str) -> Tuple[bool, str]:
        """Converte M4A → WAV usando ffmpeg."""
        cmd = [
            'ffmpeg',
            '-i', input_path,
            '-vn',  # No video
            '-acodec', 'pcm_s16le',  # Codec WAV
            '-ar', str(self.sample_rate),  # Sample rate
            '-ac', '2',  # Stereo
            '-y',  # Sovrascrivi
            output_path
        ]

        return self._run_ffmpeg(cmd, input_path, output_path, "M4A→WAV")

    def _convert_m4a_to_mp3(self, input_path: str, output_path: str) -> Tuple[bool, str]:
        """Converte M4A → MP3 usando ffmpeg."""
        cmd = [
            'ffmpeg',
            '-i', input_path,
            '-vn',  # No video
            '-codec:a', 'libmp3lame',
            '-b:a', self.bitrate,
            '-y',  # Sovrascrivi
            output_path
        ]

        return self._run_ffmpeg(cmd, input_path, output_path, "M4A→MP3")

    def _convert_wav_to_mp3(self, input_path: str, output_path: str) -> Tuple[bool, str]:
        """Converte WAV → MP3 usando pydub."""
        try:
            from pydub import AudioSegment

            audio = AudioSegment.from_wav(input_path)
            audio.export(output_path, format='mp3', bitrate=self.bitrate)

            file_size = os.path.getsize(output_path) / (1024 * 1024)
            return True, f"Conversione WAV→MP3 completata ({file_size:.2f} MB)"

        except ImportError:
            return False, "pydub non installato. Installare con: pip install pydub"
        except Exception as e:
            return False, f"Errore conversione WAV→MP3: {str(e)}"

    def _convert_wav_to_wav(self, input_path: str, output_path: str) -> Tuple[bool, str]:
        """Normalizza WAV (resampling) usando soundfile."""
        try:
            import soundfile as sf

            data, samplerate = sf.read(input_path)
            sf.write(output_path, data, self.sample_rate)

            file_size = os.path.getsize(output_path) / (1024 * 1024)
            return True, f"Normalizzazione WAV completata ({file_size:.2f} MB)"

        except ImportError:
            return False, "soundfile non installato. Installare con: pip install soundfile"
        except Exception as e:
            return False, f"Errore normalizzazione WAV: {str(e)}"

    def _convert_mp3_to_wav(self, input_path: str, output_path: str) -> Tuple[bool, str]:
        """Converte MP3 → WAV usando pydub."""
        try:
            from pydub import AudioSegment

            audio = AudioSegment.from_mp3(input_path)
            # Imposta sample rate
            audio = audio.set_frame_rate(self.sample_rate)
            audio.export(output_path, format='wav')

            file_size = os.path.getsize(output_path) / (1024 * 1024)
            return True, f"Conversione MP3→WAV completata ({file_size:.2f} MB)"

        except ImportError:
            return False, "pydub non installato. Installare con: pip install pydub"
        except Exception as e:
            return False, f"Errore conversione MP3→WAV: {str(e)}"

    def _convert_mp3_to_mp3(self, input_path: str, output_path: str) -> Tuple[bool, str]:
        """Re-encoda MP3 (cambio bitrate) usando ffmpeg."""
        cmd = [
            'ffmpeg',
            '-i', input_path,
            '-codec:a', 'libmp3lame',
            '-b:a', self.bitrate,
            '-y',  # Sovrascrivi
            output_path
        ]

        return self._run_ffmpeg(cmd, input_path, output_path, "MP3→MP3")

    def _run_ffmpeg(
        self,
        cmd: list,
        input_path: str,
        output_path: str,
        conversion_type: str
    ) -> Tuple[bool, str]:
        """Esegue comando ffmpeg e gestisce errori."""
        try:
            result = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=self.MAX_TIMEOUT
            )

            if result.returncode == 0 and os.path.exists(output_path):
                file_size = os.path.getsize(output_path) / (1024 * 1024)
                return True, f"Conversione {conversion_type} completata ({file_size:.2f} MB)"
            else:
                error_msg = result.stderr.decode('utf-8', errors='ignore')
                return False, f"Errore ffmpeg durante {conversion_type}: {error_msg[:200]}"

        except subprocess.TimeoutExpired:
            return False, f"Timeout durante conversione {conversion_type} (>{self.MAX_TIMEOUT}s)"
        except Exception as e:
            return False, f"Errore durante conversione {conversion_type}: {str(e)}"


def get_supported_conversions() -> dict:
    """Ritorna dizionario conversioni supportate."""
    return {
        'm4a': ['wav', 'mp3'],
        'wav': ['mp3', 'wav'],
        'mp3': ['wav', 'mp3'],
    }


if __name__ == '__main__':
    # Test rapido
    print("AudioConverter - Test")
    print("=" * 50)

    # Verifica ffmpeg
    if check_ffmpeg():
        print("✓ ffmpeg trovato")
    else:
        print("✗ ffmpeg non trovato")

    # Mostra conversioni supportate
    print("\nConversioni supportate:")
    for input_fmt, output_fmts in get_supported_conversions().items():
        for output_fmt in output_fmts:
            print(f"  {input_fmt} → {output_fmt}")
