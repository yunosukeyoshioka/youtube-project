"""Interface every LLM ("the brains") provider must implement."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class LLMProvider(ABC):
    """Generates text and structured JSON used by the ideation/research/script/
    marketing/analytics stages."""

    @abstractmethod
    def complete(self, system: str, prompt: str, max_tokens: int = 2000) -> str:
        """Return the raw text completion for a prompt."""

    @abstractmethod
    def generate_json(
        self, system: str, prompt: str, max_tokens: int = 2000
    ) -> dict[str, Any]:
        """Return a parsed JSON object. Implementations should instruct the
        underlying model to respond with JSON only and parse defensively."""
