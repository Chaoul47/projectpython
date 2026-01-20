Sonic Cipher
============

Overview
--------
Sonic Cipher is a Python desktop utility that hides encrypted text inside WAV audio
files using least-significant-bit (LSB) steganography. A Tkinter GUI provides
workflows to encrypt-and-hide a message or decrypt-and-reveal a message.

Features
--------
- LSB steganography for WAV audio.
- Password-based encryption using PBKDF2 + Fernet (AES in CBC with HMAC).
- Capacity checks before writing hidden data.
- Optional waveform comparison plot for visual inspection.
- Optional compression to fit longer messages.

Requirements
------------
- Python 3.10+ recommended.
- Dependencies listed in requirements.txt.

Setup
-----
1. Create and activate a virtual environment (recommended):
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
2. Install dependencies:
   pip install -r requirements.txt

Usage
-----
Run the GUI:
   python main_gui.py

Workflow: Hide Data
-------------------
1. Open the "Hide Data" tab.
2. Browse and select a WAV file.
3. Enter the secret message and password.
4. (Optional) Enable compression to fit more text.
5. Click "ENCRYPT & HIDE" and save the new WAV file.

Workflow: Reveal Data
---------------------
1. Open the "Reveal Data" tab.
2. Browse and select the stego WAV file.
3. Enter the password used for encryption.
4. Click "DECRYPT & EXTRACT" to reveal the message.

Notes
-----
- Only uncompressed WAV files are supported.
- The hidden data uses a delimiter to detect the end of the message.
- The waveform comparison tool requires matplotlib.

