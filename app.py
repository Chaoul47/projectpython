from __future__ import annotations

import os
import tempfile
from pathlib import Path

from flask import (
    Flask,
    after_this_request,
    flash,
    redirect,
    render_template,
    request,
    send_file,
    url_for,
)
from werkzeug.utils import secure_filename

from Sonic_Cipher import audio_stego, security

ALLOWED_EXTENSIONS = {".wav"}
MAX_UPLOAD_BYTES = 25 * 1024 * 1024

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = MAX_UPLOAD_BYTES
app.config["SECRET_KEY"] = os.environ.get("SONIC_CIPHER_SECRET", "dev-only-change-me")


def _make_temp_path(suffix: str) -> str:
    fd, path = tempfile.mkstemp(suffix=suffix)
    os.close(fd)
    return path


def _safe_remove(path: str | None) -> None:
    if path and os.path.exists(path):
        try:
            os.remove(path)
        except OSError:
            pass


def _cleanup_paths(*paths: str | None) -> None:
    for path in paths:
        _safe_remove(path)


def _flash_error(message: object):
    flash(str(message), "error")
    return redirect(url_for("index"))


def _save_upload(file_storage) -> tuple[str, str]:
    if file_storage is None or not file_storage.filename:
        raise ValueError("No file selected.")

    filename = secure_filename(file_storage.filename)
    ext = Path(filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise ValueError("Only .wav files are supported.")

    temp_path = _make_temp_path(ext)
    file_storage.save(temp_path)
    return temp_path, filename


@app.route("/", methods=["GET"])
def index() -> str:
    return render_template("index.html", decrypted_message=None)


@app.route("/hide", methods=["POST"])
def hide() -> "flask.wrappers.Response":
    message = request.form.get("message", "")
    password = request.form.get("password", "")
    upload = request.files.get("audio")

    input_path = None
    output_path = None
    try:
        input_path, original_name = _save_upload(upload)
        encrypted = security.encrypt_message(message, password)
        capacity = audio_stego.calculate_capacity(input_path)
        if len(encrypted) > capacity:
            raise ValueError(
                f"Encrypted payload too large for this audio. Capacity: {capacity} bytes."
            )

        output_path = _make_temp_path(".wav")
        audio_stego.hide_data(input_path, output_path, encrypted, password)
        download_name = f"{Path(original_name).stem}_secret.wav"

        @after_this_request
        def _cleanup(response):
            _cleanup_paths(input_path, output_path)
            return response

        return send_file(
            output_path,
            as_attachment=True,
            download_name=download_name,
            mimetype="audio/wav",
        )
    except Exception as exc:
        _cleanup_paths(input_path, output_path)
        return _flash_error(exc)


@app.route("/reveal", methods=["POST"])
def reveal() -> str:
    password = request.form.get("password", "")
    upload = request.files.get("audio")

    input_path = None
    try:
        input_path, _ = _save_upload(upload)
        payload = audio_stego.extract_data(input_path, password)
        message = security.decrypt_message(payload, password)
        return render_template("index.html", decrypted_message=message)
    except Exception as exc:
        return _flash_error(exc)
    finally:
        _cleanup_paths(input_path)


if __name__ == "__main__":
    app.run(debug=True, port=5000)
