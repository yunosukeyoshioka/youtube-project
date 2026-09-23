from pathlib import Path

import yaml
from click.testing import CliRunner

from youtube_automation.cli import cli

BASE_CONFIG = {
    "channel": {
        "name": "Base Channel",
        "niche": "unit test niche",
        "audience": "testers",
        "tone": "neutral",
        "language": "en",
        "video_length_seconds": 20,
    },
    "providers": {
        "llm": "mock",
        "tts": "silent",
        "image": "local",
        "research": "llm_knowledge",
        "video": "ffmpeg",
        "youtube": "dry_run",
    },
    "data_dir": "data",
}


def test_discover_channels_save_then_create_via_channel_flag():
    runner = CliRunner()
    with runner.isolated_filesystem():
        with open("config.yaml", "w", encoding="utf-8") as fh:
            yaml.safe_dump(BASE_CONFIG, fh)

        discover_result = runner.invoke(
            cli, ["--config", "config.yaml", "discover-channels", "--count", "2", "--save"]
        )
        assert discover_result.exit_code == 0, discover_result.output

        channel_files = sorted(Path("channels").glob("*.yaml"))
        assert len(channel_files) == 2

        channels_result = runner.invoke(cli, ["channels"])
        assert channels_result.exit_code == 0
        for f in channel_files:
            assert f.stem in channels_result.output

        slug = channel_files[0].stem
        create_result = runner.invoke(
            cli, ["--channel", slug, "create", "--no-publish"]
        )
        assert create_result.exit_code == 0, create_result.output
        assert "Project:" in create_result.output

        video_files = list(Path(f"data/channels/{slug}/projects").rglob("video.mp4"))
        assert len(video_files) == 1
        assert video_files[0].stat().st_size > 1000


def test_create_fails_clearly_for_unknown_channel():
    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(cli, ["--channel", "does-not-exist", "create"])
        assert result.exit_code != 0
        assert "does-not-exist" in result.output
