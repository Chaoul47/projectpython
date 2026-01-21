# Sonic Cipher

[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](#requirements)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![CI](https://github.com/Chaoul47/projectpython/actions/workflows/ci.yml/badge.svg)](https://github.com/Chaoul47/projectpython/actions/workflows/ci.yml)

Sonic Cipher hides encrypted messages inside WAV audio files using LSB steganography.
You can run it as a Tkinter desktop app or as a Flask web app.

## Features
- AES-256 encryption (Fernet) with password-based key derivation (PBKDF2 + salt)
- Adaptive LSB embedding on high-energy samples for better stealth
- Password-keyed random embedding positions for extraction control
- WAV-only workflow for lossless recovery
- Desktop (Tkinter) and web (Flask) interfaces

## Project Structure
```
Sonic_Cipher/
  audio_stego.py
  security.py
  main_gui.py
app.py
templates/
static/
```

## Requirements
- Python 3.10+
- pip

## Install Dependencies
```powershell
py -3 -m venv .venv
.\.venv\Scripts\python -m pip install -r requirements.txt
```

## Run the Tkinter Desktop App
```powershell
.\.venv\Scripts\python Sonic_Cipher\main_gui.py
```

Optional launcher:
```powershell
scripts\Run_Sonic_Cipher.bat
```

Desktop shortcut:
```powershell
powershell -ExecutionPolicy Bypass -File scripts\Create_Desktop_Shortcut.ps1
```

## Run the Flask Web App (Local)
```powershell
.\.venv\Scripts\python app.py
```
Open: http://127.0.0.1:5000

Optional launcher:
```powershell
scripts\Run_Sonic_Cipher_Web.bat
```

## Deploy on Render
- Build command: `pip install -r requirements.txt`
- Start command: `gunicorn app:app`
- Optional env var: `SONIC_CIPHER_SECRET` (Flask secret key)

## Security Notes
- Encrypt-before-hide ensures confidentiality even if the stego is detected.
- Fernet provides authenticated encryption to detect tampering.
- Passwords are never stored.

## Limitations
- Only uncompressed PCM WAV files are supported.
- Lossy formats (MP3, AAC) will destroy the hidden payload.

## Contributing
See `CONTRIBUTING.md`.

## License
MIT - see `LICENSE`.
