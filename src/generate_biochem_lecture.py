#!/usr/bin/env python3
"""
Script per generare audio di lezioni di biochimica con pronuncia corretta.

Integra il preprocessore di testo biochimico con il modello TTS configurato
per voce accademica inglese.
"""

import argparse
import json
import torch
import soundfile as sf
from pathlib import Path
from biochem_text_preprocessor import BiochemTextPreprocessor
from qwen_tts import Qwen3TTSModel


def load_config(config_path: str) -> dict:
    """Carica configurazione da file JSON."""
    with open(config_path, 'r') as f:
        return json.load(f)


def generate_biochem_lecture(
    input_text: str,
    output_path: str,
    config_path: str = "config/voice_config_academic_biochem_en.json",
    custom_mappings: dict = None,
    use_preprocessing: bool = True
):
    """
    Genera audio di lezione biochimica.

    Args:
        input_text: Testo della lezione (può essere path a file .txt o stringa)
        output_path: Path del file audio output
        config_path: Path configurazione vocale
        custom_mappings: Mappings personalizzati opzionali per terminologia
        use_preprocessing: Se True, preprocessa il testo per terminologia scientifica
    """
    # 1. Carica configurazione
    config = load_config(config_path)
    print(f"Loaded voice config: {config_path}")

    # 2. Leggi testo input
    if Path(input_text).exists():
        with open(input_text, 'r', encoding='utf-8') as f:
            text = f.read()
        print(f"Loaded text from: {input_text}")
    else:
        text = input_text
        print("Using provided text string")

    # 3. Preprocessa testo se richiesto
    if use_preprocessing:
        preprocessor = BiochemTextPreprocessor()
        if custom_mappings:
            preprocessor.add_custom_mappings(custom_mappings, category="custom")

        original_text = text
        text = preprocessor.preprocess(text)

        print("\n=== Text Preprocessing ===")
        print(f"Original length: {len(original_text)} chars")
        print(f"Processed length: {len(text)} chars")
        print("\nFirst 200 chars of processed text:")
        print(text[:200] + "...\n")

    # 4. Carica modello TTS
    print("Loading TTS model...")

    # Determina attn_implementation basato su disponibilità flash-attn
    try:
        import flash_attn
        attn_impl = "flash_attention_2"
        print("Using Flash Attention 2")
    except ImportError:
        attn_impl = "eager"
        print("Flash Attention 2 not available, using eager implementation")

    model = Qwen3TTSModel.from_pretrained(
        "Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign",
        device_map="mps",  # Metal Performance Shaders per M3 Max
        dtype=torch.bfloat16,
        attn_implementation=attn_impl,
    )
    print("Model loaded successfully")

    # 5. Genera audio
    print("\nGenerating audio...")
    wavs, sr = model.generate_voice_design(
        text=text,
        language=config["language"],
        instruct=config["voice_description"],
    )

    # 6. Salva audio
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Determina formato da configurazione
    output_format = config.get("output_format", "wav")
    if output_format == "wav":
        sf.write(str(output_path), wavs[0], sr)
        print(f"\nAudio saved to: {output_path}")
    elif output_format == "mp3":
        # Salva temporaneamente come WAV poi converti
        temp_wav = output_path.with_suffix('.wav')
        sf.write(str(temp_wav), wavs[0], sr)

        # Converti a MP3 (richiede pydub e ffmpeg)
        try:
            from pydub import AudioSegment
            audio = AudioSegment.from_wav(str(temp_wav))
            audio.export(str(output_path.with_suffix('.mp3')),
                        format="mp3",
                        bitrate="192k")
            temp_wav.unlink()  # Rimuovi WAV temporaneo
            print(f"\nAudio saved to: {output_path.with_suffix('.mp3')}")
        except ImportError:
            print("Warning: pydub not installed. Saving as WAV instead.")
            print(f"\nAudio saved to: {temp_wav}")

    print(f"Sample rate: {sr} Hz")
    print(f"Duration: {len(wavs[0])/sr:.2f} seconds")


def main():
    parser = argparse.ArgumentParser(
        description="Generate biochemistry lecture audio with correct pronunciation"
    )
    parser.add_argument(
        "-i", "--input",
        required=True,
        help="Input text file or text string"
    )
    parser.add_argument(
        "-o", "--output",
        required=True,
        help="Output audio file path"
    )
    parser.add_argument(
        "-c", "--config",
        default="config/voice_config_academic_biochem_en.json",
        help="Voice configuration file"
    )
    parser.add_argument(
        "--no-preprocess",
        action="store_true",
        help="Disable biochemical text preprocessing"
    )
    parser.add_argument(
        "--preview-preprocessing",
        action="store_true",
        help="Preview preprocessed text without generating audio"
    )

    args = parser.parse_args()

    # Preview mode
    if args.preview_preprocessing:
        if Path(args.input).exists():
            with open(args.input, 'r', encoding='utf-8') as f:
                text = f.read()
        else:
            text = args.input

        preprocessor = BiochemTextPreprocessor()
        processed = preprocessor.preprocess(text)

        print("=== Original Text ===")
        print(text)
        print("\n=== Processed Text ===")
        print(processed)
        return

    # Genera audio
    generate_biochem_lecture(
        input_text=args.input,
        output_path=args.output,
        config_path=args.config,
        use_preprocessing=not args.no_preprocess
    )


if __name__ == "__main__":
    main()
