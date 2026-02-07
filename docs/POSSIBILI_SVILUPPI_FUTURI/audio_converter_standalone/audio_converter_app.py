#!/usr/bin/env python3
"""
Flask Web App per conversione formati audio.
Interfaccia web user-friendly con drag-and-drop per convertire M4A/WAV/MP3.
"""

import os
import uuid
import shutil
import argparse
from pathlib import Path
from flask import Flask, request, jsonify, send_file, render_template
from werkzeug.utils import secure_filename

from audio_converter import AudioConverter, check_ffmpeg, get_supported_conversions


# Configurazione app
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max upload
app.config['UPLOAD_FOLDER'] = '/tmp/audio_converter_uploads'
app.config['OUTPUT_FOLDER'] = '/tmp/audio_converter_outputs'

# Formati supportati
ALLOWED_EXTENSIONS = {'m4a', 'wav', 'mp3'}


def allowed_file(filename: str) -> bool:
    """Verifica se l'estensione file è supportata."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def get_file_extension(filename: str) -> str:
    """Estrae estensione da filename."""
    return filename.rsplit('.', 1)[1].lower() if '.' in filename else ''


def cleanup_session_files(session_id: str):
    """Rimuove file temporanei di una sessione."""
    upload_dir = Path(app.config['UPLOAD_FOLDER']) / session_id
    output_dir = Path(app.config['OUTPUT_FOLDER']) / session_id

    for dir_path in [upload_dir, output_dir]:
        if dir_path.exists():
            try:
                shutil.rmtree(dir_path)
            except Exception as e:
                print(f"⚠ Errore cleanup {dir_path}: {e}")


@app.route('/')
def index():
    """Serve interfaccia web."""
    return render_template('audio_converter.html')


@app.route('/health')
def health():
    """Health check endpoint."""
    ffmpeg_ok = check_ffmpeg()
    return jsonify({
        'status': 'ok' if ffmpeg_ok else 'error',
        'ffmpeg': ffmpeg_ok,
        'supported_conversions': get_supported_conversions()
    })


@app.route('/convert', methods=['POST'])
def convert():
    """
    Endpoint principale per conversione audio.
    Riceve file upload, esegue conversione, ritorna file convertito.
    """
    # Verifica presenza file
    if 'file' not in request.files:
        return jsonify({'error': 'Nessun file caricato'}), 400

    file = request.files['file']

    # Verifica filename
    if file.filename == '':
        return jsonify({'error': 'Nome file vuoto'}), 400

    # Verifica estensione
    if not allowed_file(file.filename):
        return jsonify({
            'error': f'Formato non supportato. Formati accettati: {", ".join(ALLOWED_EXTENSIONS)}'
        }), 400

    # Leggi formato output richiesto
    output_format = request.form.get('output_format', '').lower()
    if output_format not in ALLOWED_EXTENSIONS:
        return jsonify({'error': f'Formato output non valido: {output_format}'}), 400

    # Genera session ID
    session_id = str(uuid.uuid4())

    # Crea directory temporanee
    upload_dir = Path(app.config['UPLOAD_FOLDER']) / session_id
    output_dir = Path(app.config['OUTPUT_FOLDER']) / session_id
    upload_dir.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)

    try:
        # Salva file upload
        filename = secure_filename(file.filename)
        input_path = upload_dir / filename
        file.save(str(input_path))

        # Verifica dimensione file salvato
        file_size_mb = input_path.stat().st_size / (1024 * 1024)
        if file_size_mb > 50:
            cleanup_session_files(session_id)
            return jsonify({'error': f'File troppo grande: {file_size_mb:.1f}MB (max 50MB)'}), 400

        # Genera nome output
        input_format = get_file_extension(filename)
        output_filename = f"{Path(filename).stem}.{output_format}"
        output_path = output_dir / output_filename

        # Esegui conversione
        converter = AudioConverter()
        success, message = converter.convert(
            str(input_path),
            str(output_path),
            input_format,
            output_format
        )

        if not success:
            cleanup_session_files(session_id)
            return jsonify({'error': message}), 500

        # Invia file convertito
        response = send_file(
            str(output_path),
            as_attachment=True,
            download_name=output_filename,
            mimetype=f'audio/{output_format}'
        )

        # Cleanup asincrono (dopo invio risposta)
        @response.call_on_close
        def cleanup():
            cleanup_session_files(session_id)

        return response

    except Exception as e:
        cleanup_session_files(session_id)
        return jsonify({'error': f'Errore durante conversione: {str(e)}'}), 500


@app.errorhandler(413)
def request_entity_too_large(error):
    """Gestisce errore file troppo grande."""
    return jsonify({'error': 'File troppo grande (max 50MB)'}), 413


@app.errorhandler(500)
def internal_error(error):
    """Gestisce errori interni."""
    return jsonify({'error': 'Errore interno del server'}), 500


def main():
    """Entry point principale."""
    parser = argparse.ArgumentParser(description='Audio Converter Web App')
    parser.add_argument('--port', type=int, default=5000, help='Porta server (default: 5000)')
    parser.add_argument('--debug', action='store_true', help='Modalità debug')
    parser.add_argument('--host', default='127.0.0.1', help='Host (default: 127.0.0.1)')
    args = parser.parse_args()

    # Verifica ffmpeg
    if not check_ffmpeg():
        print("✗ ERRORE: ffmpeg non trovato")
        print("  Installare con: brew install ffmpeg")
        return 1

    # Banner
    print("\n" + "=" * 50)
    print("🎵 Audio Converter Web App")
    print("=" * 50)
    print(f"Server running at: http://{args.host}:{args.port}")
    print("Formati supportati: M4A, WAV, MP3")
    print("Press Ctrl+C to stop")
    print("=" * 50 + "\n")

    # Avvia server
    app.run(
        host=args.host,
        port=args.port,
        debug=args.debug
    )

    return 0


if __name__ == '__main__':
    exit(main())
