"""Interface for gathering supporting facts/sources for a video topic."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class SearchResult:
    title: str
    url: str
    snippet: str


class ResearchProvider(ABC):
    @abstractmethod
    def search(self, query: str, max_results: int = 5) -> list[SearchResult]:
        """Return web search results relevant to `query`. Providers with no web
        access should return an empty list rather than raising, so the
        research stage can fall back to the LLM's own knowledge."""
