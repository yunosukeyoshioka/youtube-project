from ...config import AppConfig
from .anthropic_provider import AnthropicProvider
from .base import LLMProvider
from .mock_provider import MockLLMProvider

__all__ = ["LLMProvider", "AnthropicProvider", "MockLLMProvider", "build_llm_provider"]


def build_llm_provider(config: AppConfig) -> LLMProvider:
    name = config.providers.llm
    if name == "mock":
        return MockLLMProvider()
    if name == "anthropic":
        return AnthropicProvider(
            api_key=config.anthropic_api_key, model=config.anthropic_model
        )
    raise ValueError(f"Unknown LLM provider: {name!r}")
