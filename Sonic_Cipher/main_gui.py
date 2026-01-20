"""Tkinter GUI for Sonic Cipher."""

from __future__ import annotations

import tkinter as tk
from pathlib import Path
from typing import Optional
from tkinter import filedialog, messagebox, ttk

import audio_stego
import security


class SonicCipherApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Sonic Cipher")
        self.minsize(720, 520)

        self.hide_input_path = tk.StringVar(value="")
        self.hide_capacity_var = tk.StringVar(value="Capacity: -")
        self.hide_message_len_var = tk.StringVar(value="Message length: 0 chars")
        self.hide_password_var = tk.StringVar(value="")
        self.hide_capacity_bytes = 0

        self.reveal_input_path = tk.StringVar(value="")
        self.reveal_password_var = tk.StringVar(value="")

        self._build_ui()

    def _build_ui(self) -> None:
        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True, padx=12, pady=12)

        hide_tab = ttk.Frame(notebook)
        reveal_tab = ttk.Frame(notebook)
        notebook.add(hide_tab, text="Hide Data")
        notebook.add(reveal_tab, text="Reveal Data")

        self._build_hide_tab(hide_tab)
        self._build_reveal_tab(reveal_tab)

        tools_frame = ttk.Frame(self)
        tools_frame.pack(fill="x", padx=12, pady=(0, 12))
        ttk.Button(
            tools_frame, text="Compare Waveforms", command=self._compare_waveforms
        ).pack(side="right")

    def _build_hide_tab(self, parent: ttk.Frame) -> None:
        file_frame = ttk.LabelFrame(parent, text="Input WAV")
        file_frame.pack(fill="x", padx=8, pady=8)
        ttk.Button(file_frame, text="Browse", command=self._select_hide_input).pack(
            side="left", padx=8, pady=8
        )
        ttk.Label(file_frame, textvariable=self.hide_input_path).pack(
            side="left", padx=8
        )

        meta_frame = ttk.Frame(parent)
        meta_frame.pack(fill="x", padx=8)
        ttk.Label(meta_frame, textvariable=self.hide_capacity_var).pack(
            side="left", padx=4
        )
        ttk.Label(meta_frame, textvariable=self.hide_message_len_var).pack(
            side="left", padx=12
        )

        msg_frame = ttk.LabelFrame(parent, text="Secret Message")
        msg_frame.pack(fill="both", expand=True, padx=8, pady=8)
        self.hide_message_text = tk.Text(msg_frame, height=10, wrap="word")
        self.hide_message_text.pack(fill="both", expand=True, padx=8, pady=8)
        self.hide_message_text.bind("<KeyRelease>", self._update_message_length)

        pwd_frame = ttk.LabelFrame(parent, text="Password")
        pwd_frame.pack(fill="x", padx=8, pady=8)
        ttk.Entry(pwd_frame, textvariable=self.hide_password_var, show="*").pack(
            fill="x", padx=8, pady=8
        )

        ttk.Button(
            parent, text="ENCRYPT & HIDE", command=self._handle_hide
        ).pack(pady=6)

    def _build_reveal_tab(self, parent: ttk.Frame) -> None:
        file_frame = ttk.LabelFrame(parent, text="Secret WAV")
        file_frame.pack(fill="x", padx=8, pady=8)
        ttk.Button(file_frame, text="Browse", command=self._select_reveal_input).pack(
            side="left", padx=8, pady=8
        )
        ttk.Label(file_frame, textvariable=self.reveal_input_path).pack(
            side="left", padx=8
        )

        pwd_frame = ttk.LabelFrame(parent, text="Password")
        pwd_frame.pack(fill="x", padx=8, pady=8)
        ttk.Entry(pwd_frame, textvariable=self.reveal_password_var, show="*").pack(
            fill="x", padx=8, pady=8
        )

        ttk.Button(
            parent, text="DECRYPT & EXTRACT", command=self._handle_reveal
        ).pack(pady=6)

        out_frame = ttk.LabelFrame(parent, text="Decrypted Message")
        out_frame.pack(fill="both", expand=True, padx=8, pady=8)
        self.reveal_message_text = tk.Text(out_frame, height=10, wrap="word")
        self.reveal_message_text.pack(fill="both", expand=True, padx=8, pady=8)
        self.reveal_message_text.configure(state="disabled")

    def _select_hide_input(self) -> None:
        path = filedialog.askopenfilename(
            title="Select WAV File",
            filetypes=[("WAV files", "*.wav")],
        )
        if not path:
            return

        self.hide_input_path.set(path)
        try:
            self.hide_capacity_bytes = audio_stego.calculate_capacity(path)
            self.hide_capacity_var.set(f"Capacity: {self.hide_capacity_bytes} bytes")
        except Exception as exc:
            messagebox.showerror("Error", str(exc))
            self.hide_capacity_bytes = 0
            self.hide_capacity_var.set("Capacity: -")

    def _select_reveal_input(self) -> None:
        path = filedialog.askopenfilename(
            title="Select WAV File",
            filetypes=[("WAV files", "*.wav")],
        )
        if not path:
            return
        self.reveal_input_path.set(path)

    def _update_message_length(self, _event: Optional[tk.Event] = None) -> None:
        text = self.hide_message_text.get("1.0", "end-1c")
        self.hide_message_len_var.set(f"Message length: {len(text)} chars")

    def _handle_hide(self) -> None:
        wav_path = self.hide_input_path.get()
        if not wav_path:
            messagebox.showerror("Error", "Select a WAV file first.")
            return

        message = self.hide_message_text.get("1.0", "end-1c")
        password = self.hide_password_var.get()

        try:
            encrypted = security.encrypt_message(message, password)
        except security.SecurityError as exc:
            messagebox.showerror("Error", str(exc))
            return

        try:
            capacity = audio_stego.calculate_capacity(wav_path)
        except Exception as exc:
            messagebox.showerror("Error", str(exc))
            return

        if len(encrypted) > capacity:
            messagebox.showerror(
                "Error",
                f"Encrypted payload is too large. Capacity: {capacity} bytes.",
            )
            return

        default_name = Path(wav_path).with_suffix("").name + "_secret.wav"
        out_path = filedialog.asksaveasfilename(
            title="Save Stego WAV",
            defaultextension=".wav",
            initialfile=default_name,
            filetypes=[("WAV files", "*.wav")],
        )
        if not out_path:
            return

        try:
            audio_stego.hide_data(wav_path, out_path, encrypted)
        except Exception as exc:
            messagebox.showerror("Error", str(exc))
            return

        messagebox.showinfo("Success", f"File saved to:\n{out_path}")

    def _handle_reveal(self) -> None:
        wav_path = self.reveal_input_path.get()
        if not wav_path:
            messagebox.showerror("Error", "Select a WAV file first.")
            return

        password = self.reveal_password_var.get()

        try:
            payload = audio_stego.extract_data(wav_path)
        except Exception as exc:
            messagebox.showerror("Error", str(exc))
            return

        try:
            message = security.decrypt_message(payload, password)
        except security.DecryptionError as exc:
            messagebox.showerror("Error", str(exc))
            return
        except security.SecurityError as exc:
            messagebox.showerror("Error", str(exc))
            return

        self.reveal_message_text.configure(state="normal")
        self.reveal_message_text.delete("1.0", "end")
        self.reveal_message_text.insert("1.0", message)
        self.reveal_message_text.configure(state="disabled")
        messagebox.showinfo("Success", "Message decrypted successfully.")

    def _compare_waveforms(self) -> None:
        orig_path = filedialog.askopenfilename(
            title="Select Original WAV",
            filetypes=[("WAV files", "*.wav")],
        )
        if not orig_path:
            return
        steg_path = filedialog.askopenfilename(
            title="Select Stego WAV",
            filetypes=[("WAV files", "*.wav")],
        )
        if not steg_path:
            return

        try:
            audio_stego.plot_waveform_comparison(orig_path, steg_path)
        except Exception as exc:
            messagebox.showerror("Error", str(exc))


def main() -> None:
    app = SonicCipherApp()
    app.mainloop()


if __name__ == "__main__":
    main()
