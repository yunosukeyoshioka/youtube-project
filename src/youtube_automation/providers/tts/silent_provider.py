"""Last-resort TTS provider: writes silence timed to the narration length.
Pure stdlib, always succeeds, so the pipeline can still assemble a correctly
timed (if voiceless) video when no speech engine is available at all. The
on-screen captions carry the narration in that case."""

from __future__ import annotations

import wave

from .base import TTSProvider, estimate_duration_seconds

SAMPLE_RATE = 16_000


class SilentPlaceholderTTSProvider(TTSProvider):
    def synthesize(self, text: str, output_path: str) -> float:
        duration = estimate_duration_seconds(text)
        n_frames = int(duration * SAMPLE_RATE)
        with wave.open(output_path, "wb") as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(SAMPLE_RATE)
            wav_file.writeframes(b"\x00\x00" * n_frames)
        return duration
