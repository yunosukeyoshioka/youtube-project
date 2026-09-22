"""Fully offline, no-API-key TTS provider backed by the espeak-ng CLI. Good
default so the pipeline can produce a real narrated video with zero paid
services configured."""

from __future__ import annotations

import shutil
import subprocess
import wave

from .base import TTSProvider, estimate_duration_seconds


def espeak_available() -> bool:
    return shutil.which("espeak-ng") is not None or shutil.which("espeak") is not None


class EspeakTTSProvider(TTSProvider):
    def __init__(self, voice: str = "en", speed_wpm: int = 165) -> None:
        self._binary = shutil.which("espeak-ng") or shutil.which("espeak")
        if not self._binary:
            raise RuntimeError(
                "espeak-ng is not installed. Install it (e.g. `apt-get install "
                "espeak-ng`) or choose a different TTS provider."
            )
        self._voice = voice
        self._speed_wpm = speed_wpm

    def synthesize(self, text: str, output_path: str) -> float:
        subprocess.run(
            [
                self._binary,
                "-v",
                self._voice,
                "-s",
                str(self._speed_wpm),
                "-w",
                output_path,
                text,
            ],
            check=True,
            capture_output=True,
        )
        try:
            with wave.open(output_path, "rb") as wav_file:
                frames = wav_file.getnframes()
                rate = wav_file.getframerate()
                return round(frames / float(rate), 2) if rate else estimate_duration_seconds(text)
        except (wave.Error, FileNotFoundError):
            return estimate_duration_seconds(text)
