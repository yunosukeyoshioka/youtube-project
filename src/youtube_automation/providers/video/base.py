"""Interface for assembling per-scene image+audio pairs into a final video."""

from __future__ import annotations

from abc import ABC, abstractmethod

from ...models import SceneAsset


class VideoAssembler(ABC):
    @abstractmethod
    def assemble(
        self,
        scene_assets: list[SceneAsset],
        scene_captions: list[str],
        output_path: str,
    ) -> str:
        """Combine scenes (each an image + narration audio, already rendered to
        disk) into a single video file at `output_path`. `scene_captions` are
        the narration lines burned in as on-screen subtitles, aligned by
        index with `scene_assets`. Returns `output_path`."""
