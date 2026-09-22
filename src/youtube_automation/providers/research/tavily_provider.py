"""Web research via the Tavily search API (https://tavily.com). Requires
TAVILY_API_KEY. Falls back gracefully (empty results) on any network/API
error so the pipeline never hard-fails because of a flaky third party."""

from __future__ import annotations

import logging

import requests

from .base import ResearchProvider, SearchResult

logger = logging.getLogger(__name__)

TAVILY_ENDPOINT = "https://api.tavily.com/search"


class TavilyResearchProvider(ResearchProvider):
    def __init__(self, api_key: str, timeout_seconds: float = 15.0) -> None:
        self._api_key = api_key
        self._timeout = timeout_seconds

    def search(self, query: str, max_results: int = 5) -> list[SearchResult]:
        try:
            response = requests.post(
                TAVILY_ENDPOINT,
                json={
                    "api_key": self._api_key,
                    "query": query,
                    "max_results": max_results,
                },
                timeout=self._timeout,
            )
            response.raise_for_status()
            payload = response.json()
        except Exception:  # noqa: BLE001 - any failure degrades to no results
            logger.warning("Tavily search failed for query=%r", query, exc_info=True)
            return []

        results = []
        for item in payload.get("results", [])[:max_results]:
            results.append(
                SearchResult(
                    title=item.get("title", ""),
                    url=item.get("url", ""),
                    snippet=item.get("content", ""),
                )
            )
        return results
