"""Default publisher: never actually uploads anything. Lets the full pipeline
run safely (including in CI/tests) until you deliberately configure real
YouTube OAuth credentials and switch `providers.youtube` to `youtube_api`."""

from __future__ import annotations

import logging

from ...models import MarketingPackage, PublishResult
from .base import YouTubePublisher

logger = logging.getLogger(__name__)


class DryRunPublisher(YouTubePublisher):
    def publish(
        self,
        video_path: str,
        thumbnail_path: str,
        marketing: MarketingPackage,
        privacy_status: str = "private",
    ) -> PublishResult:
        logger.info(
            "[dry-run] Would upload %s (thumbnail=%s, title=%r, privacy=%s)",
            video_path,
            thumbnail_path,
            marketing.chosen_title,
            privacy_status,
        )
        return PublishResult(
            published=False,
            reason=(
                "Dry-run mode: set providers.youtube: youtube_api and configure "
                "OAuth credentials in config.yaml to publish for real."
            ),
        )
