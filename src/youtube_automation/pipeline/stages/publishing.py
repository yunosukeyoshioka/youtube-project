"""Stage 7: publishing. Uploads the finished video (and thumbnail) to
YouTube, or performs a dry run depending on configuration."""

from __future__ import annotations

from ...models import VideoProject
from ...providers.youtube.base import YouTubePublisher


class PublishingStage:
    def __init__(self, publisher: YouTubePublisher, privacy_status: str = "private") -> None:
        self._publisher = publisher
        self._privacy_status = privacy_status

    def run(self, project: VideoProject) -> None:
        assert project.production is not None, "Production must run before publishing."
        assert project.marketing is not None

        result = self._publisher.publish(
            video_path=project.production.video_path,
            thumbnail_path=project.production.thumbnail.path,
            marketing=project.marketing,
            privacy_status=self._privacy_status,
        )
        project.publish_result = result
        if result.published:
            project.log(f"Publishing: uploaded as {result.url}.")
        else:
            project.log(f"Publishing: skipped ({result.reason}).")
