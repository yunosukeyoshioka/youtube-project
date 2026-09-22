"""Interface for producing scene visuals and the video thumbnail."""

from __future__ import annotations

from abc import ABC, abstractmethod


class ImageProvider(ABC):
    @abstractmethod
    def generate_scene_image(
        self, on_screen_text: str, visual_direction: str, output_path: str
    ) -> None:
        """Render (or fetch) the visual for one script scene to `output_path`."""

    @abstractmethod
    def generate_thumbnail(self, title: str, concept: str, output_path: str) -> None:
        """Render (or fetch) the video thumbnail to `output_path`."""
