from ...config import AppConfig
from .analytics import YouTubeStatsReader
from .base import YouTubePublisher
from .dry_run_provider import DryRunPublisher
from .youtube_api_provider import YouTubeApiPublisher

__all__ = [
    "YouTubePublisher",
    "DryRunPublisher",
    "YouTubeApiPublisher",
    "YouTubeStatsReader",
    "build_youtube_publisher",
]


def build_youtube_publisher(config: AppConfig) -> YouTubePublisher:
    name = config.providers.youtube
    if name == "dry_run":
        return DryRunPublisher()
    if name == "youtube_api":
        return YouTubeApiPublisher(
            client_secrets_file=config.youtube_client_secrets_file,
            token_file=config.youtube_token_file,
        )
    raise ValueError(f"Unknown youtube provider: {name!r}")
