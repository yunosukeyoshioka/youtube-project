"""Stage 5: design. Renders the clickable thumbnail from the chosen title and
the marketing stage's thumbnail concepts."""

from __future__ import annotations

from pathlib import Path

from ...models import ThumbnailAsset, VideoProject
from ...providers.image.base import ImageProvider
from ...storage.project_store import ProjectStore


class DesignStage:
    def __init__(self, image_provider: ImageProvider, project_store: ProjectStore) -> None:
        self._image_provider = image_provider
        self._store = project_store

    def run(self, project: VideoProject) -> ThumbnailAsset:
        assert project.marketing is not None, "Marketing must run before design."
        concept = (
            project.marketing.thumbnail_concepts[0]
            if project.marketing.thumbnail_concepts
            else project.marketing.chosen_title
        )
        thumbnail_path = str(
            Path(self._store.project_dir(project.project_id)) / "thumbnail.png"
        )
        self._image_provider.generate_thumbnail(
            title=project.marketing.chosen_title,
            concept=concept,
            output_path=thumbnail_path,
        )
        project.log(f"Design: rendered thumbnail at {thumbnail_path}.")
        return ThumbnailAsset(path=thumbnail_path, concept=concept)
