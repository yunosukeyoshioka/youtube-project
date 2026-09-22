from ...config import AppConfig
from .base import VideoAssembler
from .ffmpeg_assembler import FfmpegVideoAssembler

__all__ = ["VideoAssembler", "FfmpegVideoAssembler", "build_video_assembler"]


def build_video_assembler(config: AppConfig) -> VideoAssembler:
    name = config.providers.video
    if name == "ffmpeg":
        return FfmpegVideoAssembler()
    raise ValueError(f"Unknown video provider: {name!r}")
