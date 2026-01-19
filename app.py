from __future__ import annotations

import sqlite3
from datetime import datetime
from pathlib import Path

from cryptography.fernet import Fernet, InvalidToken
from flask import Flask, jsonify, render_template, request

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "messages.db"

app = Flask(__name__)


def init_db() -> None:
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ciphertext TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.commit()


init_db()


def store_message(ciphertext: str) -> int:
    timestamp = datetime.utcnow().isoformat(timespec="seconds") + "Z"
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.execute(
            "INSERT INTO messages (ciphertext, created_at) VALUES (?, ?)",
            (ciphertext, timestamp),
        )
        conn.commit()
        return int(cursor.lastrowid)


def fetch_message(message_id: int) -> tuple[int, str, str] | None:
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.execute(
            "SELECT id, ciphertext, created_at FROM messages WHERE id = ?",
            (message_id,),
        )
        row = cursor.fetchone()
    if row is None:
        return None
    return int(row[0]), str(row[1]), str(row[2])


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/encrypt", methods=["POST"])
def encrypt_message():
    payload = request.get_json(silent=True) or {}
    message = (payload.get("message") or "").strip()
    key = (payload.get("key") or "").strip()

    if not message:
        return jsonify({"error": "Message cannot be empty."}), 400
    if not key:
        return jsonify({"error": "Key is required for encryption."}), 400

    try:
        fernet = Fernet(key.encode("utf-8"))
        ciphertext = fernet.encrypt(message.encode("utf-8")).decode("utf-8")
    except (ValueError, TypeError):
        return jsonify({"error": "Key must be a valid Fernet key."}), 400

    message_id = store_message(ciphertext)
    return jsonify({"id": message_id, "created_at": datetime.utcnow().isoformat(timespec="seconds") + "Z"})


@app.route("/api/decrypt", methods=["POST"])
def decrypt_message():
    payload = request.get_json(silent=True) or {}
    message_id = payload.get("id")
    key = (payload.get("key") or "").strip()

    if message_id is None:
        return jsonify({"error": "Message ID is required."}), 400
    if not key:
        return jsonify({"error": "Key is required for decryption."}), 400

    try:
        message_id_int = int(message_id)
    except (ValueError, TypeError):
        return jsonify({"error": "Message ID must be a number."}), 400

    message_row = fetch_message(message_id_int)
    if message_row is None:
        return jsonify({"error": "Message not found."}), 404

    _, ciphertext, created_at = message_row
    try:
        fernet = Fernet(key.encode("utf-8"))
        plaintext = fernet.decrypt(ciphertext.encode("utf-8")).decode("utf-8")
    except (InvalidToken, ValueError, TypeError):
        return jsonify({"error": "Invalid key for this message."}), 400

    return jsonify({"message": plaintext, "created_at": created_at})


@app.route("/api/messages", methods=["GET"])
def list_messages():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.execute("SELECT id, created_at FROM messages ORDER BY id DESC")
        messages = [
            {"id": int(row[0]), "created_at": str(row[1])} for row in cursor.fetchall()
        ]
    return jsonify({"messages": messages})


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=True)
