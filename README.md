# Sonic Cipher

Sonic Cipher hides encrypted messages inside WAV audio files using LSB steganography.
You can run it as a Tkinter desktop app or as a Flask web app.

## Requirements
- Python 3.10+
- pip

## Install dependencies (recommended)
```powershell
py -3 -m venv .venv
.\.venv\Scripts\python -m pip install -r requirements.txt
```

## Run the Tkinter desktop app
```powershell
.\.venv\Scripts\python Sonic_Cipher\main_gui.py
```

Optional launcher:
```powershell
Run_Sonic_Cipher.bat
```

## Run the Flask web app
```powershell
.\.venv\Scripts\python app.py
```
Open: http://127.0.0.1:5000

Optional launcher:
```powershell
Run_Sonic_Cipher_Web.bat
```

## Notes
- Use uncompressed PCM .wav files only (MP3 and compressed WAVs will not work).
