from pathlib import Path

from youtube_automation.config import ProviderConfig, load_config
from youtube_automation.models import ChannelConcept
from youtube_automation.storage.channel_config_writer import write_channel_config


def test_write_channel_config_produces_a_loadable_config(tmp_path: Path):
    concept = ChannelConcept(
        name="Quick Curiosity!",
        niche="60-second science facts",
        audience="curious teens",
        tone="playful",
        positioning="shorter than existing explainer channels",
        content_pillars=["myth busting", "weird history"],
        sample_video_titles=["Why the Sky Isn't Blue"],
        reasoning="Gap in short-form science content.",
        language="en",
        video_length_seconds=60,
    )
    providers = ProviderConfig(
        llm="mock", tts="silent", image="local", research="llm_knowledge", video="ffmpeg",
        youtube="dry_run",
    )

    path = write_channel_config(concept, tmp_path / "channels", providers)

    assert path.name == "quick-curiosity.yaml"
    assert path.exists()

    loaded = load_config(path)
    assert loaded.channel.name == "Quick Curiosity!"
    assert loaded.channel.niche == "60-second science facts"
    assert loaded.channel.video_length_seconds == 60
    assert loaded.providers.llm == "mock"
    assert loaded.data_dir == Path("data/channels/quick-curiosity")
