#!/usr/bin/env python3
"""
Script per generare audio con voice cloning usando Qwen3-TTS.
Clona la voce da un campione audio di riferimento (3-10 secondi).
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
        return False
    except Exception as e:
        print(f"⚠ Errore conversione MP3: {e}")
        return False


def preprocess_text_biochimica(text):
    """
    Preprocessa testo con terminologia biochimica.

    Returns:
        Tuple[str, bool]: (testo_processato, preprocessing_applicato)
    """
    try:
        from biochem_text_preprocessor import BiochemTextPreprocessor
        preprocessor = BiochemTextPreprocessor()
        processed_text = preprocessor.process_text(text)
        return processed_text, True
    except ImportError:
        print("⚠ Preprocessor biochimica non disponibile")
        return text, False
    except Exception as e:
        print(f"⚠ Errore preprocessing: {e}")
        return text, False


def generate_cloned_audio(
    input_file,
    output_file,
    config_path,
    model=None,
    use_biochem_preprocessor=False,
    preview_preprocessing=False
):
    """
    Genera audio usando voice cloning da campione vocale.

    Args:
        input_file: Path al file di testo input
        output_file: Path al file audio output
        config_path: Path al file di configurazione
        model: Modello pre-caricato (opzionale)
        use_biochem_preprocessor: Se True, applica preprocessing biochimica
        preview_preprocessing: Se True, mostra preview preprocessing senza generare audio

    Returns:
        model se caricato in questa funzione, True se successo, False altrimenti
    """
    # Carica configurazione
    config = load_config(config_path)
    language = config.get('language', 'Italian')
    prompt_speech_path = config.get('prompt_speech_path')
    output_format = config.get('output_format', 'wav')
    voice_notes = config.get('voice_notes', '')

    # Verifica presenza campione audio
    if not prompt_speech_path:
        print("❌ Errore: 'prompt_speech_path' non specificato nel file di configurazione")
        return False

    if not os.path.exists(prompt_speech_path):
        print(f"❌ Errore: Campione audio non trovato: {prompt_speech_path}")
        return False

    # Leggi testo
    print(f"📖 Lettura testo da: {input_file}")
    text = read_text_file(input_file)
    if not text:
        print("❌ Errore: file di testo vuoto")
        return False

    # Preprocessing opzionale
    preprocessing_applied = False
    if use_biochem_preprocessor:
        print("🔬 Applicazione preprocessing biochimica...")
        text, preprocessing_applied = preprocess_text_biochimica(text)
        if preprocessing_applied:
            print("✓ Preprocessing applicato")

    # Preview preprocessing e esci
    if preview_preprocessing:
        print("\n" + "="*60)
        print("PREVIEW PREPROCESSING")
        print("="*60)
        print(text)
        print("="*60)
        return True

    print(f"📝 Testo da convertire ({len(text)} caratteri)")
    print(f"🗣️  Lingua: {language}")
    print(f"🎤 Campione vocale: {prompt_speech_path}")
    if voice_notes:
        print(f"📌 Note: {voice_notes}")

    # Carica modello se non fornito
    model_loaded = False
    if model is None:
        print("🔄 Caricamento modello Qwen3-TTS VoiceClone...")
        try:
            model = Qwen3TTSModel.from_pretrained(
                "Qwen/Qwen3-TTS-12Hz-1.7B-VoiceClone",
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
                    "Qwen/Qwen3-TTS-12Hz-1.7B-VoiceClone",
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
        print("🎵 Generazione audio in corso (voice cloning)...")
        wavs, sr = model.generate_voice_clone(
            text=text,
            language=language,
            prompt_speech=prompt_speech_path,
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
        description='Genera audio con voice cloning usando Qwen3-TTS',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Esempi:
  # Voice cloning base con config predefinita
  python generate_cloned_audio.py -i INPUT/testo.txt -c config/clone_config_speaker1.json

  # Specifica output esplicito
  python generate_cloned_audio.py -i INPUT/testo.txt -c config/clone_config_speaker1.json -o OUTPUT/cloned.wav

  # Con preprocessing biochimica
  python generate_cloned_audio.py -i INPUT/biochemistry.txt -c config/clone_config.json --use-biochem-preprocessor

  # Preview preprocessing senza generare audio
  python generate_cloned_audio.py -i INPUT/biochemistry.txt -c config/clone_config.json --preview-preprocessing
        """
    )

    parser.add_argument(
        '--input', '-i',
        required=True,
        help='Path al file di testo input'
    )

    parser.add_argument(
        '--output', '-o',
        help='Path al file audio output (default: OUTPUT/[nome_input]_cloned.wav)'
    )

    parser.add_argument(
        '--config', '-c',
        required=True,
        help='Path al file di configurazione voice cloning (es. config/clone_config_speaker1.json)'
    )

    parser.add_argument(
        '--use-biochem-preprocessor',
        action='store_true',
        help='Applica preprocessing per terminologia scientifica/biochimica'
    )

    parser.add_argument(
        '--preview-preprocessing',
        action='store_true',
        help='Mostra preview del preprocessing senza generare audio'
    )

    args = parser.parse_args()

    # Determina path output se non specificato
    if args.output is None:
        input_name = Path(args.input).stem
        args.output = f"OUTPUT/{input_name}_cloned.wav"

    # Verifica file input esista
    if not os.path.exists(args.input):
        print(f"❌ Errore: file input non trovato: {args.input}")
        sys.exit(1)

    # Verifica file config esista
    if not os.path.exists(args.config):
        print(f"❌ Errore: file configurazione non trovato: {args.config}")
        print(f"💡 Crea un file di configurazione voice cloning in: {args.config}")
        print("   Esempio:")
        print('   {')
        print('     "mode": "voice_clone",')
        print('     "language": "Italian",')
        print('     "prompt_speech_path": "VOICE_SAMPLES/speaker.wav",')
        print('     "output_format": "wav"')
        print('   }')
        sys.exit(1)

    # Genera audio
    success = generate_cloned_audio(
        args.input,
        args.output,
        args.config,
        use_biochem_preprocessor=args.use_biochem_preprocessor,
        preview_preprocessing=args.preview_preprocessing
    )
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
