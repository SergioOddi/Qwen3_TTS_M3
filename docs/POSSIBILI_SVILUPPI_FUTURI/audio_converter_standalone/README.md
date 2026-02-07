# Audio Converter Standalone App

Progetto per convertire `audio_converter_app.py` in app standalone macOS (.app)

## Cosa fa

Web app Flask con interfaccia drag-and-drop per convertire formati audio:
- **Input**: M4A, WAV, MP3
- **Output**: M4A, WAV, MP3
- **Dipendenze**: Flask, ffmpeg, audio_converter module

## Obiettivo

Creare app macOS standalone con doppio click, senza bisogno di:
- Ambiente virtuale Python
- Terminale
- Comandi `python` o `conda activate`

## Soluzione Proposta: PyInstaller

### 1. Setup PyInstaller

```bash
# Attiva ambiente virtuale
conda activate qwen3-tts

# Installa PyInstaller
pip install pyinstaller
```

### 2. Bundle ffmpeg

```bash
# Copia ffmpeg nel progetto
cp $(which ffmpeg) .
```

### 3. Crea spec file

Creare `audio_converter_app.spec`:

```python
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['audio_converter_app.py'],
    pathex=[],
    binaries=[
        ('ffmpeg', '.'),  # Include ffmpeg binary
    ],
    datas=[
        ('templates', 'templates'),  # Include HTML templates
    ],
    hiddenimports=['flask', 'werkzeug'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='AudioConverter',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # No terminal window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='AudioConverter',
)

app = BUNDLE(
    coll,
    name='AudioConverter.app',
    icon=None,  # Opzionale: aggiungere icona .icns
    bundle_identifier='com.tts.audioconverter',
)
```

### 4. Build App

```bash
pyinstaller audio_converter_app.spec
```

Output: `dist/AudioConverter.app`

### 5. Aggiungi Auto-open Browser

Modificare `audio_converter_app.py` per aprire browser automaticamente:

```python
import webbrowser
import threading

def open_browser():
    """Apre browser dopo 1.5 secondi."""
    import time
    time.sleep(1.5)
    webbrowser.open('http://127.0.0.1:5000')

# In main(), prima di app.run():
threading.Thread(target=open_browser, daemon=True).start()
```

## Risultato Finale

Doppio click su `AudioConverter.app` →
- Server Flask si avvia in background
- Browser si apre automaticamente su http://127.0.0.1:5000
- Interfaccia drag-and-drop per convertire audio

## Alternative

### Nuitka (più veloce)
```bash
pip install nuitka
python -m nuitka --standalone --onefile \
  --include-data-dir=templates=templates \
  --macos-create-app-bundle \
  audio_converter_app.py
```

### Electron (più complesso)
- Wrapper HTML/CSS/JS attorno a backend Python
- Bundle più pesante (~150MB)
- UI più personalizzabile

## Tempo Stimato

- **PyInstaller**: 2-3 ore
  - Setup e configurazione: 1h
  - Testing e debugging: 1-2h

- **Nuitka**: 3-4 ore

## Note

- Dimensione app finale: ~80-120MB (include Python runtime + dipendenze + ffmpeg)
- Compatibilità: macOS arm64 (M3 Max)
- Richiede code signing per distribuzione (opzionale per uso personale)
