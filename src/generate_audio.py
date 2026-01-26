#!/usr/bin/env python3
"""
Script per generare audio da file di testo usando Qwen3-TTS.
Supporta configurazioni personalizzate per voice design.
"""

import argparse
import json
import os
import sys
from pathlib import Path

import torch
import soundfile as sf
from qwen_tts import Qwen3TTSModel


def load_config(config_path):
    """Carica configurazione da file JSON."""
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def read_text_file(text_path):
    """Legge contenuto del file di testo."""
    with open(text_path, 'r', encoding='utf-8') as f:
        return f.read().strip()


def convert_wav_to_mp3(wav_path, mp3_path, bitrate='192k'):
    """Converte file WAV in MP3 usando pydub."""
    try:
        from pydub import AudioSegment
        audio = AudioSegment.from_wav(wav_path)
        audio.export(mp3_path, format='mp3', bitrate=bitrate)
        print(f"✓ File MP3 generato: {mp3_path}")
        return True
    except ImportError:
        print("⚠ pydub non installato. Saltando conversione MP3.")
        print("  Installare con: pip install pydub")
        print("  Richiede anche ffmpeg: brew install ffmpeg")
        return False
    except Exception as e:
        print(f"⚠ Errore conversione MP3: {e}")
        return False


def generate_audio(input_file, output_file, config_path, model=None):
    """
    Genera audio da file di testo.

    Args:
        input_file: Path al file di testo input
        output_file: Path al file audio output
        config_path: Path al file di configurazione
        model: Modello pre-caricato (opzionale)

    Returns:
        True se successo, False altrimenti
    """
    # Carica configurazione
    config = load_config(config_path)
    language = config.get('language', 'Italian')
    voice_description = config.get('voice_description', 'Voce neutra e chiara')
    output_format = config.get('output_format', 'wav')

    # Leggi testo
    print(f"📖 Lettura testo da: {input_file}")
    text = read_text_file(input_file)
    if not text:
        print("❌ Errore: file di testo vuoto")
        return False

    print(f"📝 Testo da convertire ({len(text)} caratteri)")
    print(f"🗣️  Lingua: {language}")
    print(f"🎤 Voice design: {voice_description}")

    # Carica modello se non fornito
    model_loaded = False
    if model is None:
        print("🔄 Caricamento modello Qwen3-TTS...")
        try:
            model = Qwen3TTSModel.from_pretrained(
                "Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign",
                device_map="mps",  # Metal Performance Shaders per M3 Max
                dtype=torch.bfloat16,
                attn_implementation="flash_attention_2",  # se disponibile
            )
            model_loaded = True
            print("✓ Modello caricato con successo")
        except Exception as e:
            print(f"⚠ Flash Attention 2 non disponibile, uso implementazione standard")
            try:
                model = Qwen3TTSModel.from_pretrained(
                    "Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign",
                    device_map="mps",
                    dtype=torch.bfloat16,
                )
                model_loaded = True
                print("✓ Modello caricato con successo")
            except Exception as e2:
                print(f"❌ Errore caricamento modello: {e2}")
                return False

    # Genera audio
    try:
        print("🎵 Generazione audio in corso...")
        wavs, sr = model.generate_voice_design(
            text=text,
            language=language,
            instruct=voice_description,
        )

        # Salva file WAV
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        wav_file = str(output_path.with_suffix('.wav'))
        sf.write(wav_file, wavs[0], sr)
        print(f"✓ File WAV generato: {wav_file}")

        # Converti in MP3 se richiesto
        if output_format.lower() == 'mp3':
            mp3_file = str(output_path.with_suffix('.mp3'))
            if convert_wav_to_mp3(wav_file, mp3_file):
                # Rimuovi WAV se MP3 creato con successo
                os.remove(wav_file)
                print(f"✓ File WAV temporaneo rimosso")

        print("✅ Generazione completata con successo!")
        return model if model_loaded else True

    except Exception as e:
        print(f"❌ Errore durante generazione: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    parser = argparse.ArgumentParser(
        description='Genera audio da file di testo usando Qwen3-TTS'
    )
    parser.add_argument(
        '--input', '-i',
        required=True,
        help='Path al file di testo input'
    )
    parser.add_argument(
        '--output', '-o',
        help='Path al file audio output (default: OUTPUT/[nome_input].wav)'
    )
    parser.add_argument(
        '--config', '-c',
        default='config/voice_config.json',
        help='Path al file di configurazione (default: config/voice_config.json)'
    )

    args = parser.parse_args()

    # Determina path output se non specificato
    if args.output is None:
        input_name = Path(args.input).stem
        args.output = f"OUTPUT/{input_name}.wav"

    # Verifica file input esista
    if not os.path.exists(args.input):
        print(f"❌ Errore: file input non trovato: {args.input}")
        sys.exit(1)

    # Verifica file config esista
    if not os.path.exists(args.config):
        print(f"❌ Errore: file configurazione non trovato: {args.config}")
        print(f"💡 Crea un file di configurazione in: {args.config}")
        sys.exit(1)

    # Genera audio
    success = generate_audio(args.input, args.output, args.config)
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
