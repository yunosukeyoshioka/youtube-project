"""Reads back performance stats for previously published videos, used by the
improvement/feedback loop. Uses the same OAuth credentials as the publisher
(read-only stats need no extra scope beyond youtube.readonly)."""

from __future__ import annotations

from datetime import datetime, timezone

from ...models import PerformanceSnapshot


class YouTubeStatsReader:
    def __init__(self, client_secrets_file: str, token_file: str) -> None:
        self._client_secrets_file = client_secrets_file
        self._token_file = token_file

    def fetch(self, video_id: str) -> PerformanceSnapshot:
        from googleapiclient.discovery import build

        from .youtube_api_provider import YouTubeApiPublisher

        publisher = YouTubeApiPublisher(self._client_secrets_file, self._token_file)
        youtube = build("youtube", "v3", credentials=publisher._get_credentials())
        response = (
            youtube.videos().list(part="statistics", id=video_id).execute()
        )
        items = response.get("items", [])
        stats = items[0]["statistics"] if items else {}
        return PerformanceSnapshot(
            video_id=video_id,
            captured_at=datetime.now(timezone.utc).isoformat(),
            views=int(stats.get("viewCount", 0)),
            likes=int(stats.get("likeCount", 0)),
            comments=int(stats.get("commentCount", 0)),
        )
