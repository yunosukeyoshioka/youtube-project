"""Research provider backed by the YouTube Data API v3 (simple API key, no
OAuth needed). Used by the channel-strategy stage to ground new channel
proposals in real competitor data: actual subscriber counts, view counts,
and the titles of currently popular videos/channels for a topic -- not just
the LLM's static training knowledge."""

from __future__ import annotations

import logging

from .base import ResearchProvider, SearchResult

logger = logging.getLogger(__name__)


class YouTubeDataResearchProvider(ResearchProvider):
    def __init__(self, api_key: str) -> None:
        self._api_key = api_key

    def _client(self):
        from googleapiclient.discovery import build

        return build("youtube", "v3", developerKey=self._api_key)

    def search(self, query: str, max_results: int = 5) -> list[SearchResult]:
        try:
            youtube = self._client()
            channel_results = self._top_channels(youtube, query, max(2, max_results // 2))
            video_results = self._top_videos(youtube, query, max_results - len(channel_results))
        except Exception:  # noqa: BLE001 - degrade to no results on any API failure
            logger.warning("YouTube Data API research failed for query=%r", query, exc_info=True)
            return []
        return (channel_results + video_results)[:max_results]

    def _top_channels(self, youtube, query: str, max_results: int) -> list[SearchResult]:
        search_response = (
            youtube.search()
            .list(part="snippet", q=query, type="channel", order="relevance", maxResults=max_results)
            .execute()
        )
        channel_ids = [item["snippet"]["channelId"] for item in search_response.get("items", [])]
        if not channel_ids:
            return []
        stats_response = (
            youtube.channels().list(part="snippet,statistics", id=",".join(channel_ids)).execute()
        )
        results = []
        for item in stats_response.get("items", []):
            stats = item.get("statistics", {})
            snippet = item.get("snippet", {})
            results.append(
                SearchResult(
                    title=snippet.get("title", ""),
                    url=f"https://www.youtube.com/channel/{item['id']}",
                    snippet=(
                        f"登録者数: {stats.get('subscriberCount', '非公開')} / "
                        f"総再生回数: {stats.get('viewCount', '不明')} / "
                        f"動画本数: {stats.get('videoCount', '不明')} -- "
                        f"{snippet.get('description', '')[:150]}"
                    ),
                )
            )
        return results

    def _top_videos(self, youtube, query: str, max_results: int) -> list[SearchResult]:
        if max_results <= 0:
            return []
        search_response = (
            youtube.search()
            .list(part="snippet", q=query, type="video", order="viewCount", maxResults=max_results)
            .execute()
        )
        results = []
        for item in search_response.get("items", []):
            video_id = item["id"]["videoId"]
            snippet = item["snippet"]
            results.append(
                SearchResult(
                    title=snippet.get("title", ""),
                    url=f"https://www.youtube.com/watch?v={video_id}",
                    snippet=f"チャンネル: {snippet.get('channelTitle', '')}",
                )
            )
        return results
