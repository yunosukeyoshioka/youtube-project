"""Fallback research provider used when no web-search API key is configured.
Returns no search results; the research stage then relies on the LLM's own
training knowledge and clearly labels the brief as unverified."""

from __future__ import annotations

from .base import ResearchProvider, SearchResult


class LLMKnowledgeResearchProvider(ResearchProvider):
    def search(self, query: str, max_results: int = 5) -> list[SearchResult]:
        return []
