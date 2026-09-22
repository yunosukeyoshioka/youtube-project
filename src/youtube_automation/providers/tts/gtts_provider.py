"""TTS via Google Translate's free endpoint (gTTS library). No API key
needed, but requires outbound internet access. Falls back to a duration
estimate since mp3 duration isn't trivially readable without extra deps."""

from __future__ import annotations

from .base import TTSProvider, estimate_duration_seconds


class GoogleTTSProvider(TTSProvider):
    def __init__(self, language: str = "en") -> None:
        self._language = language

    def synthesize(self, text: str, output_path: str) -> float:
        from gtts import gTTS

        gTTS(text=text, lang=self._language).save(output_path)
        return estimate_duration_seconds(text)
