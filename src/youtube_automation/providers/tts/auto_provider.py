"""Tries a preference-ordered chain of TTS providers and falls back to the
next one on any failure, so a flaky network or a missing binary never stops
video production."""

from __future__ import annotations

import logging

from .base import TTSProvider

logger = logging.getLogger(__name__)


class AutoTTSProvider(TTSProvider):
    def __init__(self, providers: list[TTSProvider]) -> None:
        if not providers:
            raise ValueError("AutoTTSProvider requires at least one candidate provider.")
        self._providers = providers

    def synthesize(self, text: str, output_path: str) -> float:
        last_error: Exception | None = None
        for provider in self._providers:
            try:
                return provider.synthesize(text, output_path)
            except Exception as exc:  # noqa: BLE001 - deliberately broad, we fall back
                logger.warning(
                    "TTS provider %s failed, falling back: %s",
                    type(provider).__name__,
                    exc,
                )
                last_error = exc
        raise RuntimeError("All TTS providers failed") from last_error
