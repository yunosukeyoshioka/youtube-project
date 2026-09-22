from ...config import AppConfig
from .base import ImageProvider
from .local_provider import LocalImageProvider
from .openai_provider import OpenAIImageProvider

__all__ = ["ImageProvider", "LocalImageProvider", "OpenAIImageProvider", "build_image_provider"]


def build_image_provider(config: AppConfig) -> ImageProvider:
    name = config.providers.image
    if name == "local":
        return LocalImageProvider()
    if name == "openai":
        if not config.image_provider_api_key:
            raise ValueError("OPENAI_API_KEY is required for the openai image provider.")
        return OpenAIImageProvider(api_key=config.image_provider_api_key)
    raise ValueError(f"Unknown image provider: {name!r}")
