"""Interface for turning narration text into an audio file."""

from __future__ import annotations

from abc import ABC, abstractmethod


def estimate_duration_seconds(text: str, words_per_minute: float = 150.0) -> float:
    word_count = max(1, len(text.split()))
    return round((word_count / words_per_minute) * 60.0, 2)


class TTSProvider(ABC):
    @abstractmethod
    def synthesize(self, text: str, output_path: str) -> float:
        """Write narration audio for `text` to `output_path` and return its
        duration in seconds."""
