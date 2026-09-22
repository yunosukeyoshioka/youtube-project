from ...config import AppConfig
from .auto_provider import AutoTTSProvider
from .base import TTSProvider, estimate_duration_seconds
from .elevenlabs_provider import ElevenLabsTTSProvider
from .espeak_provider import EspeakTTSProvider, espeak_available
from .gtts_provider import GoogleTTSProvider
from .silent_provider import SilentPlaceholderTTSProvider

__all__ = [
    "TTSProvider",
    "estimate_duration_seconds",
    "EspeakTTSProvider",
    "GoogleTTSProvider",
    "ElevenLabsTTSProvider",
    "SilentPlaceholderTTSProvider",
    "AutoTTSProvider",
    "build_tts_provider",
]


def build_tts_provider(config: AppConfig) -> TTSProvider:
    name = config.providers.tts
    language = config.channel.language

    if name == "espeak":
        return EspeakTTSProvider(voice=language)
    if name == "gtts":
        return GoogleTTSProvider(language=language)
    if name == "elevenlabs":
        if not config.tts_provider_api_key:
            raise ValueError("ELEVENLABS_API_KEY is required for the elevenlabs TTS provider.")
        return ElevenLabsTTSProvider(api_key=config.tts_provider_api_key)
    if name == "silent":
        return SilentPlaceholderTTSProvider()
    if name == "auto":
        chain: list[TTSProvider] = []
        if config.tts_provider_api_key:
            try:
                chain.append(ElevenLabsTTSProvider(api_key=config.tts_provider_api_key))
            except Exception:  # noqa: BLE001
                pass
        if espeak_available():
            chain.append(EspeakTTSProvider(voice=language))
        chain.append(GoogleTTSProvider(language=language))
        chain.append(SilentPlaceholderTTSProvider())
        return AutoTTSProvider(chain)
    raise ValueError(f"Unknown TTS provider: {name!r}")
