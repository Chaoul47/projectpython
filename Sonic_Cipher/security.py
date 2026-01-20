"""Security module for Sonic Cipher.

Handles password-based key derivation and authenticated encryption.
"""

from __future__ import annotations

import base64
import os
import zlib

from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

SALT_SIZE = 16
KDF_ITERATIONS = 200_000
MIN_PASSWORD_LENGTH = 8
MAGIC_HEADER = b"SC1"
FLAG_COMPRESSED = 0x01


class SecurityError(Exception):
    """Base class for security-related errors."""


class DecryptionError(SecurityError):
    """Raised when decryption fails or data is corrupted."""


def _validate_password(password: str) -> bytes:
    if not isinstance(password, str):
        raise SecurityError("Password must be a string.")
    if not password or not password.strip():
        raise SecurityError("Password cannot be empty.")
    if len(password) < MIN_PASSWORD_LENGTH:
        raise SecurityError(
            f"Password must be at least {MIN_PASSWORD_LENGTH} characters."
        )
    return password.encode("utf-8")


def _validate_plaintext(plaintext: str) -> bytes:
    if not isinstance(plaintext, str):
        raise SecurityError("Message must be a string.")
    if plaintext == "":
        raise SecurityError("Message cannot be empty.")
    try:
        return plaintext.encode("utf-8")
    except UnicodeEncodeError as exc:
        raise SecurityError("Message must be valid UTF-8 text.") from exc


def _derive_key(password: str, salt: bytes) -> bytes:
    if not isinstance(salt, (bytes, bytearray)) or len(salt) != SALT_SIZE:
        raise SecurityError("Invalid salt.")

    password_bytes = _validate_password(password)
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=bytes(salt),
        iterations=KDF_ITERATIONS,
    )
    return base64.urlsafe_b64encode(kdf.derive(password_bytes))


def encrypt_message(plaintext: str, password: str, compress: bool = False) -> bytes:
    """Encrypt plaintext using a password-derived key.

    Returns: magic + flags + salt + fernet_token (versioned payload).
    """

    plaintext_bytes = _validate_plaintext(plaintext)
    if compress:
        plaintext_bytes = zlib.compress(plaintext_bytes)
    salt = os.urandom(SALT_SIZE)
    key = _derive_key(password, salt)
    token = Fernet(key).encrypt(plaintext_bytes)
    flags = FLAG_COMPRESSED if compress else 0
    return MAGIC_HEADER + bytes([flags]) + salt + token


def decrypt_message(payload: bytes, password: str) -> str:
    """Decrypt payload using the password."""

    if not isinstance(payload, (bytes, bytearray)):
        raise DecryptionError("Encrypted payload must be bytes.")
    if len(payload) <= SALT_SIZE:
        raise DecryptionError("Encrypted payload is too short.")

    if payload.startswith(MAGIC_HEADER):
        if len(payload) <= len(MAGIC_HEADER) + 1 + SALT_SIZE:
            raise DecryptionError("Encrypted payload is too short.")
        flags = payload[len(MAGIC_HEADER)]
        salt_start = len(MAGIC_HEADER) + 1
        salt = payload[salt_start : salt_start + SALT_SIZE]
        token = payload[salt_start + SALT_SIZE :]
        compressed = bool(flags & FLAG_COMPRESSED)
    else:
        salt = payload[:SALT_SIZE]
        token = payload[SALT_SIZE:]
        compressed = False
    key = _derive_key(password, salt)

    try:
        plaintext_bytes = Fernet(key).decrypt(token)
    except InvalidToken as exc:
        raise DecryptionError("Wrong password or corrupted data.") from exc
    if compressed:
        try:
            plaintext_bytes = zlib.decompress(plaintext_bytes)
        except zlib.error as exc:
            raise DecryptionError("Decompression failed for payload.") from exc

    try:
        return plaintext_bytes.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise DecryptionError("Decrypted data is not valid UTF-8.") from exc

