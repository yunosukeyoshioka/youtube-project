"""Interface for publishing the finished video to YouTube."""

from __future__ import annotations

from abc import ABC, abstractmethod

from ...models import MarketingPackage, PublishResult


class YouTubePublisher(ABC):
    @abstractmethod
    def publish(
        self,
        video_path: str,
        thumbnail_path: str,
        marketing: MarketingPackage,
        privacy_status: str = "private",
    ) -> PublishResult:
        """Upload the video (and thumbnail) to YouTube."""
