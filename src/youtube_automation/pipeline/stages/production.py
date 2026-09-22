"""Stage 6: video production. Synthesizes narration audio and a visual for
every scene, then assembles them (plus the thumbnail from the design stage)
into the final video file."""

from __future__ import annotations

from pathlib import Path

from ...models import ProductionOutput, SceneAsset, ThumbnailAsset, VideoProject
from ...providers.image.base import ImageProvider
from ...providers.tts.base import TTSProvider
from ...providers.video.base import VideoAssembler
from ...storage.project_store import ProjectStore


class ProductionStage:
    def __init__(
        self,
        tts_provider: TTSProvider,
        image_provider: ImageProvider,
        video_assembler: VideoAssembler,
        project_store: ProjectStore,
    ) -> None:
        self._tts = tts_provider
        self._image_provider = image_provider
        self._assembler = video_assembler
        self._store = project_store

    def run(self, project: VideoProject, thumbnail: ThumbnailAsset) -> None:
        assert project.script is not None, "Script must run before production."

        scenes_dir = self._store.scenes_dir(project.project_id)
        scene_assets: list[SceneAsset] = []
        captions: list[str] = []

        for scene in project.script.scenes:
            audio_path = str(scenes_dir / f"scene_{scene.index:03d}.wav")
            image_path = str(scenes_dir / f"scene_{scene.index:03d}.png")

            duration = self._tts.synthesize(scene.narration, audio_path)
            self._image_provider.generate_scene_image(
                on_screen_text=scene.on_screen_text,
                visual_direction=scene.visual_direction,
                output_path=image_path,
            )
            scene_assets.append(
                SceneAsset(
                    scene_index=scene.index,
                    image_path=image_path,
                    audio_path=audio_path,
                    duration_seconds=duration,
                )
            )
            captions.append(scene.narration)

        video_path = str(Path(self._store.project_dir(project.project_id)) / "video.mp4")
        self._assembler.assemble(scene_assets, captions, video_path)

        project.production = ProductionOutput(
            video_path=video_path,
            scene_assets=scene_assets,
            thumbnail=thumbnail,
        )
        total_duration = sum(s.duration_seconds for s in scene_assets)
        project.log(
            f"Production: rendered {len(scene_assets)} scenes into {video_path} "
            f"(~{total_duration:.0f}s)."
        )
