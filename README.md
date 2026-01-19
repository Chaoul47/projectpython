# Secure Message Vault

Secure Message Vault is a simple web app that lets users encrypt a message with a shared key,
store it on the server, and decrypt it later using the same key.

## Features

- Browser-side key generation
- Server-side encryption/decryption using Fernet (symmetric encryption)
- SQLite persistence for stored messages

## Getting Started

1. Create a virtual environment and install dependencies:

   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. Run the app:

   ```bash
   python app.py
   ```

3. Visit `http://localhost:5000`.

## Security Notes

- The server never stores your plaintext message, only the encrypted ciphertext.
- Anyone with the message ID and the key can decrypt the message, so keep the key secret.
- For production use, serve the app over HTTPS and manage keys in a secure way.
