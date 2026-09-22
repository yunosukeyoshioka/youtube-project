"""LLM provider backed by the Anthropic Claude API."""

from __future__ import annotations

import json
import re
from typing import Any

from .base import LLMProvider

_JSON_FENCE_RE = re.compile(r"```(?:json)?\s*(.*?)\s*```", re.DOTALL)


def extract_json(text: str) -> dict[str, Any]:
    """Best-effort extraction of a JSON object from an LLM response, tolerating
    surrounding prose or markdown code fences."""

    fence_match = _JSON_FENCE_RE.search(text)
    candidate = fence_match.group(1) if fence_match else text.strip()
    try:
        return json.loads(candidate)
    except json.JSONDecodeError:
        pass

    start = candidate.find("{")
    end = candidate.rfind("}")
    if start != -1 and end != -1 and end > start:
        return json.loads(candidate[start : end + 1])
    raise ValueError(f"Could not extract JSON from LLM response: {text[:300]!r}")


class AnthropicProvider(LLMProvider):
    def __init__(self, api_key: str, model: str = "claude-sonnet-5") -> None:
        if not api_key:
            raise ValueError(
                "ANTHROPIC_API_KEY is required to use the Anthropic LLM provider. "
                "Set it in your environment or .env file."
            )
        import anthropic  # imported lazily so the package is optional at import time

        self._client = anthropic.Anthropic(api_key=api_key)
        self._model = model

    def complete(self, system: str, prompt: str, max_tokens: int = 2000) -> str:
        response = self._client.messages.create(
            model=self._model,
            max_tokens=max_tokens,
            system=system,
            messages=[{"role": "user", "content": prompt}],
        )
        return "".join(
            block.text for block in response.content if block.type == "text"
        )

    def generate_json(
        self, system: str, prompt: str, max_tokens: int = 2000
    ) -> dict[str, Any]:
        json_system = (
            f"{system}\n\n"
            "Respond with a single valid JSON object only. No prose, no markdown "
            "code fences, no explanation before or after the JSON."
        )
        text = self.complete(json_system, prompt, max_tokens=max_tokens)
        return extract_json(text)
