"""Loads app configuration from config.yaml plus environment variable overrides."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

try:  # pragma: no cover - optional convenience
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:  # pragma: no cover
    pass

DEFAULT_CONFIG_PATH = Path("config.yaml")
CHANNELS_DIR = Path("channels")


@dataclass
class ChannelConfig:
    name: str = "My Automated Channel"
    niche: str = "general educational shorts"
    audience: str = "general YouTube audience"
    tone: str = "energetic, clear, concise"
    language: str = "en"
    video_length_seconds: int = 90


@dataclass
class ProviderConfig:
    llm: str = "anthropic"
    tts: str = "auto"
    image: str = "local"
    research: str = "llm_knowledge"
    video: str = "ffmpeg"
    youtube: str = "dry_run"


@dataclass
class AppConfig:
    channel: ChannelConfig = field(default_factory=ChannelConfig)
    providers: ProviderConfig = field(default_factory=ProviderConfig)
    data_dir: Path = Path("data")
    anthropic_model: str = "claude-sonnet-5"
    anthropic_api_key: str | None = None
    youtube_client_secrets_file: str | None = None
    youtube_token_file: str = "data/youtube_token.json"
    research_api_key: str | None = None
    image_provider_api_key: str | None = None
    tts_provider_api_key: str | None = None
    youtube_data_api_key: str | None = None
    raw: dict[str, Any] = field(default_factory=dict)

    @property
    def projects_dir(self) -> Path:
        return self.data_dir / "projects"

    @property
    def knowledge_base_path(self) -> Path:
        return self.data_dir / "knowledge_base.json"


def _get_env(*names: str) -> str | None:
    for name in names:
        value = os.environ.get(name)
        if value:
            return value
    return None


def load_config(path: str | Path | None = None) -> AppConfig:
    """Load config.yaml (if present) and layer environment variable overrides on top."""

    config_path = Path(path) if path else DEFAULT_CONFIG_PATH
    raw: dict[str, Any] = {}
    if config_path.exists():
        with open(config_path, encoding="utf-8") as fh:
            raw = yaml.safe_load(fh) or {}

    channel_raw = raw.get("channel", {})
    providers_raw = raw.get("providers", {})

    channel = ChannelConfig(
        name=channel_raw.get("name", ChannelConfig.name),
        niche=channel_raw.get("niche", ChannelConfig.niche),
        audience=channel_raw.get("audience", ChannelConfig.audience),
        tone=channel_raw.get("tone", ChannelConfig.tone),
        language=channel_raw.get("language", ChannelConfig.language),
        video_length_seconds=channel_raw.get(
            "video_length_seconds", ChannelConfig.video_length_seconds
        ),
    )
    providers = ProviderConfig(
        llm=providers_raw.get("llm", ProviderConfig.llm),
        tts=providers_raw.get("tts", ProviderConfig.tts),
        image=providers_raw.get("image", ProviderConfig.image),
        research=providers_raw.get("research", ProviderConfig.research),
        video=providers_raw.get("video", ProviderConfig.video),
        youtube=providers_raw.get("youtube", ProviderConfig.youtube),
    )

    return AppConfig(
        channel=channel,
        providers=providers,
        data_dir=Path(raw.get("data_dir", "data")),
        anthropic_model=_get_env("ANTHROPIC_MODEL") or raw.get(
            "anthropic_model", "claude-sonnet-5"
        ),
        anthropic_api_key=_get_env("ANTHROPIC_API_KEY"),
        youtube_client_secrets_file=raw.get(
            "youtube_client_secrets_file", "data/youtube_client_secret.json"
        ),
        youtube_token_file=raw.get("youtube_token_file", "data/youtube_token.json"),
        research_api_key=_get_env("TAVILY_API_KEY", "SERPER_API_KEY"),
        image_provider_api_key=_get_env("OPENAI_API_KEY", "STABILITY_API_KEY"),
        tts_provider_api_key=_get_env("ELEVENLABS_API_KEY", "OPENAI_API_KEY"),
        youtube_data_api_key=_get_env("YOUTUBE_API_KEY"),
        raw=raw,
    )


def channel_config_path(slug: str, channels_dir: Path = CHANNELS_DIR) -> Path:
    return channels_dir / f"{slug}.yaml"
