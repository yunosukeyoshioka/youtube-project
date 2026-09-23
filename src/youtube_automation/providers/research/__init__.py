from ...config import AppConfig
from .base import ResearchProvider, SearchResult
from .llm_knowledge_provider import LLMKnowledgeResearchProvider
from .tavily_provider import TavilyResearchProvider
from .youtube_data_provider import YouTubeDataResearchProvider

__all__ = [
    "ResearchProvider",
    "SearchResult",
    "TavilyResearchProvider",
    "LLMKnowledgeResearchProvider",
    "YouTubeDataResearchProvider",
    "build_research_provider",
]


def build_research_provider(config: AppConfig) -> ResearchProvider:
    name = config.providers.research
    if name == "tavily":
        if not config.research_api_key:
            raise ValueError("TAVILY_API_KEY is required for the tavily research provider.")
        return TavilyResearchProvider(api_key=config.research_api_key)
    if name == "youtube_data_api":
        if not config.youtube_data_api_key:
            raise ValueError(
                "YOUTUBE_API_KEY is required for the youtube_data_api research provider."
            )
        return YouTubeDataResearchProvider(api_key=config.youtube_data_api_key)
    if name == "llm_knowledge":
        return LLMKnowledgeResearchProvider()
    raise ValueError(f"Unknown research provider: {name!r}")
