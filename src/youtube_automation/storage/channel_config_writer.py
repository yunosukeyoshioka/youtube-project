"""Turns a ChannelConcept proposal into a ready-to-use channels/<slug>.yaml,
matching config.yaml's schema so it can immediately be used via
`youtube-automation --channel <slug> create`."""

from __future__ import annotations

from pathlib import Path

import yaml

from ..config import ProviderConfig
from ..models import ChannelConcept
from .project_store import slugify


def write_channel_config(
    concept: ChannelConcept,
    channels_dir: Path,
    providers: ProviderConfig,
    channel_data_root: str = "data/channels",
) -> Path:
    channels_dir = Path(channels_dir)
    channels_dir.mkdir(parents=True, exist_ok=True)

    slug = slugify(concept.name)
    path = channels_dir / f"{slug}.yaml"

    document = {
        "channel": {
            "name": concept.name,
            "niche": concept.niche,
            "audience": concept.audience,
            "tone": concept.tone,
            "language": concept.language,
            "video_length_seconds": concept.video_length_seconds,
        },
        "providers": {
            "llm": providers.llm,
            "tts": providers.tts,
            "image": providers.image,
            "research": providers.research,
            "video": providers.video,
            "youtube": providers.youtube,
        },
        "data_dir": f"{channel_data_root}/{slug}",
        # Reference-only: not read by the pipeline, but explains *why* this
        # concept was proposed so a human can sanity-check it before use.
        "strategy": {
            "positioning": concept.positioning,
            "content_pillars": concept.content_pillars,
            "sample_video_titles": concept.sample_video_titles,
            "reasoning": concept.reasoning,
        },
    }

    with open(path, "w", encoding="utf-8") as fh:
        yaml.safe_dump(document, fh, allow_unicode=True, sort_keys=False)

    return path
