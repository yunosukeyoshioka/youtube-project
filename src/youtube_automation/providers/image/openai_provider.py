"""Higher-quality image provider using OpenAI's image generation API.
Requires OPENAI_API_KEY. Recommended once you're ready to publish real
videos instead of the free local placeholder renderer."""

from __future__ import annotations

import base64
from pathlib import Path

import requests

from .base import ImageProvider

IMAGES_ENDPOINT = "https://api.openai.com/v1/images/generations"


class OpenAIImageProvider(ImageProvider):
    def __init__(self, api_key: str, model: str = "gpt-image-1") -> None:
        self._api_key = api_key
        self._model = model

    def _generate(self, prompt: str, output_path: str, size: str = "1536x1024") -> None:
        response = requests.post(
            IMAGES_ENDPOINT,
            headers={"Authorization": f"Bearer {self._api_key}"},
            json={"model": self._model, "prompt": prompt, "size": size},
            timeout=120,
        )
        response.raise_for_status()
        payload = response.json()
        image_b64 = payload["data"][0]["b64_json"]
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "wb") as fh:
            fh.write(base64.b64decode(image_b64))

    def generate_scene_image(
        self, on_screen_text: str, visual_direction: str, output_path: str
    ) -> None:
        prompt = (
            f"YouTube video scene illustration, cinematic, high detail: "
            f"{visual_direction}. On-screen caption context: {on_screen_text!r}. "
            "No embedded text or watermarks in the image itself."
        )
        self._generate(prompt, output_path)

    def generate_thumbnail(self, title: str, concept: str, output_path: str) -> None:
        prompt = (
            f"Bold, high-contrast, clickable YouTube thumbnail concept for a video "
            f"titled {title!r}. Visual concept: {concept}. Vibrant colors, clear "
            "focal point, no embedded text."
        )
        self._generate(prompt, output_path, size="1536x1024")
