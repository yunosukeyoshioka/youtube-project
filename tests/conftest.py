from __future__ import annotations

from pathlib import Path

import pytest

from youtube_automation.config import AppConfig, ChannelConfig, ProviderConfig


@pytest.fixture
def offline_config(tmp_path: Path) -> AppConfig:
    """A config that never touches the network or a paid API: mock LLM,
    local image renderer, silent TTS, no-op research, dry-run publishing."""

    return AppConfig(
        channel=ChannelConfig(
            name="Test Channel",
            niche="test niche",
            audience="testers",
            tone="neutral",
            language="en",
            video_length_seconds=30,
        ),
        providers=ProviderConfig(
            llm="mock",
            tts="silent",
            image="local",
            research="llm_knowledge",
            video="ffmpeg",
            youtube="dry_run",
        ),
        data_dir=tmp_path / "data",
    )
