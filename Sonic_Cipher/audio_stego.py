"""Audio steganography engine for Sonic Cipher.

Implements LSB embedding and extraction for WAV files.
"""

from __future__ import annotations

import wave
from pathlib import Path
from typing import Iterable, Tuple, Union

DELIMITER = b"###END###"
SUPPORTED_SAMPLE_WIDTHS = {1, 2, 3, 4}


class StegoError(Exception):
    """Base class for steganography errors."""


def _validate_wav_path(path: Union[str, Path]) -> Path:
    wav_path = Path(path)
    if not wav_path.exists():
        raise FileNotFoundError(f"File not found: {wav_path}")
    if wav_path.suffix.lower() != ".wav":
        raise StegoError("Only .wav files are supported.")
    return wav_path


def _validate_output_path(path: Union[str, Path]) -> Path:
    out_path = Path(path)
    if out_path.suffix.lower() != ".wav":
        raise StegoError("Output file must have a .wav extension.")
    return out_path


def _bytes_to_bits(data: bytes) -> Iterable[int]:
    for byte_val in data:
        for bit_index in range(7, -1, -1):
            yield (byte_val >> bit_index) & 1


def _bits_to_byte(bits: Iterable[int]) -> int:
    value = 0
    for bit in bits:
        value = (value << 1) | bit
    return value


def _max_payload_bytes(n_frames: int, n_channels: int) -> int:
    sample_count = n_frames * n_channels
    return sample_count // 8


def calculate_capacity(path: Union[str, Path]) -> int:
    """Return max payload bytes available for this WAV (excluding delimiter)."""

    wav_path = _validate_wav_path(path)
    with wave.open(str(wav_path), "rb") as wf:
        n_frames = wf.getnframes()
        n_channels = wf.getnchannels()
    max_payload = _max_payload_bytes(n_frames, n_channels)
    available = max_payload - len(DELIMITER)
    return max(0, available)


def _read_wave(path: Path) -> Tuple[wave._wave_params, bytearray]:
    with wave.open(str(path), "rb") as wf:
        params = wf.getparams()
        if params.sampwidth not in SUPPORTED_SAMPLE_WIDTHS:
            raise StegoError("Unsupported sample width.")
        if params.comptype != "NONE":
            raise StegoError("Compressed WAV files are not supported.")
        if params.nframes <= 0:
            raise StegoError("WAV file has no audio frames.")
        frames = wf.readframes(params.nframes)
    return params, bytearray(frames)


def _write_wave(path: Path, params: wave._wave_params, frames: bytes) -> None:
    with wave.open(str(path), "wb") as wf:
        wf.setparams(params)
        wf.writeframes(frames)


def hide_data(
    in_path: Union[str, Path], out_path: Union[str, Path], payload: bytes
) -> None:
    """Hide payload bytes inside a WAV file and write the result to out_path."""

    if not isinstance(payload, (bytes, bytearray)) or not payload:
        raise StegoError("Payload must be non-empty bytes.")

    wav_path = _validate_wav_path(in_path)
    out_path = _validate_output_path(out_path)
    if wav_path.resolve() == out_path.resolve():
        raise StegoError("Output path must be different from input path.")

    params, frame_bytes = _read_wave(wav_path)
    full_payload = bytes(payload) + DELIMITER
    required_bits = len(full_payload) * 8
    if required_bits > params.nframes * params.nchannels:
        raise StegoError(
            "Message too large for this audio file. Reduce size or use a larger WAV."
        )

    bit_iter = _bytes_to_bits(full_payload)
    samples_count = len(frame_bytes) // params.sampwidth
    for sample_index in range(samples_count):
        try:
            bit = next(bit_iter)
        except StopIteration:
            break
        byte_index = sample_index * params.sampwidth
        frame_bytes[byte_index] = (frame_bytes[byte_index] & 0xFE) | bit

    if next(bit_iter, None) is not None:
        raise StegoError("Not enough capacity to hide the message.")

    _write_wave(out_path, params, bytes(frame_bytes))


def extract_data(path: Union[str, Path]) -> bytes:
    """Extract payload bytes from a WAV file using the delimiter."""

    wav_path = _validate_wav_path(path)
    params, frame_bytes = _read_wave(wav_path)

    samples_count = len(frame_bytes) // params.sampwidth
    collected = bytearray()
    bit_buffer = []

    for sample_index in range(samples_count):
        byte_index = sample_index * params.sampwidth
        bit_buffer.append(frame_bytes[byte_index] & 1)
        if len(bit_buffer) == 8:
            collected.append(_bits_to_byte(bit_buffer))
            bit_buffer.clear()
            if collected.endswith(DELIMITER):
                return bytes(collected[:-len(DELIMITER)])

    raise StegoError("Delimiter not found. No hidden message detected.")


def plot_waveform_comparison(
    original_path: Union[str, Path],
    stego_path: Union[str, Path],
    max_points: int = 10000,
) -> None:
    """Plot waveform comparison for presentation.

    Requires matplotlib; raises StegoError if missing.
    """

    try:
        import matplotlib.pyplot as plt
    except ImportError as exc:
        raise StegoError("matplotlib is required for waveform plotting.") from exc

    orig = _validate_wav_path(original_path)
    steg = _validate_wav_path(stego_path)

    def read_samples(path: Path) -> Tuple[int, list[int]]:
        params, frame_bytes = _read_wave(path)
        step = params.sampwidth
        samples = []
        for i in range(0, len(frame_bytes), step):
            chunk = frame_bytes[i : i + step]
            if step == 1:
                # 8-bit PCM is unsigned.
                val = chunk[0] - 128
            elif step == 2:
                val = int.from_bytes(chunk, byteorder="little", signed=True)
            elif step == 3:
                val = int.from_bytes(chunk, byteorder="little", signed=True)
            else:
                val = int.from_bytes(chunk, byteorder="little", signed=True)
            samples.append(val)
        if len(samples) > max_points:
            stride = max(1, len(samples) // max_points)
            samples = samples[::stride]
        return params.framerate, samples

    rate_orig, samples_orig = read_samples(orig)
    rate_steg, samples_steg = read_samples(steg)
    if rate_orig != rate_steg:
        raise StegoError("Sample rates do not match for comparison.")

    x_orig = list(range(len(samples_orig)))
    x_steg = list(range(len(samples_steg)))

    fig, axes = plt.subplots(2, 1, figsize=(10, 6), sharex=True)
    axes[0].plot(x_orig, samples_orig, color="#1f77b4")
    axes[0].set_title("Original Waveform")
    axes[1].plot(x_steg, samples_steg, color="#ff7f0e")
    axes[1].set_title("Stego Waveform")
    for ax in axes:
        ax.set_ylabel("Amplitude")
        ax.grid(True, linestyle="--", alpha=0.4)
    axes[1].set_xlabel("Sample Index (downsampled)")
    fig.tight_layout()
    plt.show()
