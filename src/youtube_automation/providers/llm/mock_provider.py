"""Deterministic offline LLM provider used for tests and dry runs without an
Anthropic API key. It never calls the network."""

from __future__ import annotations

from typing import Any

from .base import LLMProvider


class MockLLMProvider(LLMProvider):
    def __init__(self, canned_responses: dict[str, dict[str, Any]] | None = None) -> None:
        self._canned = canned_responses or {}

    def complete(self, system: str, prompt: str, max_tokens: int = 2000) -> str:
        return "This is a mock completion used for offline testing."

    def generate_json(
        self, system: str, prompt: str, max_tokens: int = 2000
    ) -> dict[str, Any]:
        for keyword, response in self._canned.items():
            if keyword.lower() in prompt.lower():
                return response
        return self._default_response(prompt)

    @staticmethod
    def _default_response(prompt: str) -> dict[str, Any]:
        if "video idea" in prompt.lower() or "brainstorm" in prompt.lower():
            return {
                "ideas": [
                    {
                        "title": "5 Everyday Habits That Are Secretly Wasting Your Time",
                        "hook": "You are losing hours every week and don't even notice it.",
                        "angle": "relatable productivity myth-busting",
                        "target_audience": "young professionals",
                        "reasoning": "High search volume, low competition, strong hook.",
                        "virality_score": 8.2,
                        "tags": ["productivity", "life hacks", "self improvement"],
                    }
                ]
            }
        if "research brief" in prompt.lower():
            return {
                "summary": "Overview of the topic with supporting context.",
                "key_points": ["Point one", "Point two", "Point three"],
                "sources": ["internal knowledge"],
                "open_questions": [],
            }
        if "video script" in prompt.lower():
            return {
                "hook_line": "Stop scrolling, this will change how you spend your day.",
                "scenes": [
                    {
                        "narration": "Here's the first habit that's quietly wasting your time.",
                        "visual_direction": "Bold title card with the habit name.",
                        "on_screen_text": "Habit #1",
                        "duration_hint_seconds": 6,
                    },
                    {
                        "narration": "Here's how to fix it starting today.",
                        "visual_direction": "Checklist graphic.",
                        "on_screen_text": "The Fix",
                        "duration_hint_seconds": 6,
                    },
                ],
                "call_to_action": "Subscribe for more tips that actually work.",
            }
        if "marketing package" in prompt.lower():
            return {
                "title_options": [
                    "5 Habits Secretly Wasting Your Time",
                    "Stop Doing This Every Day",
                ],
                "chosen_title": "5 Habits Secretly Wasting Your Time",
                "description": "In this video we break down five habits and how to fix them.",
                "tags": ["productivity", "self improvement", "life hacks"],
                "hashtags": ["#productivity", "#lifehacks"],
                "thumbnail_concepts": [
                    "Shocked face with a clock graphic and bold red text."
                ],
            }
        if "insights about" in prompt.lower():
            return {
                "insights": [
                    "Shorter hooks under 3 seconds retained more viewers.",
                    "Numbered list titles outperformed question titles.",
                ]
            }
        return {}
