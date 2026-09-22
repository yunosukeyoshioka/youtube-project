"""Core data structures shared across the pipeline stages."""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Any


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class VideoIdea:
    title: str
    hook: str
    angle: str
    target_audience: str
    reasoning: str
    virality_score: float
    tags: list[str] = field(default_factory=list)


@dataclass
class ResearchBrief:
    summary: str
    key_points: list[str]
    sources: list[str]
    open_questions: list[str] = field(default_factory=list)


@dataclass
class ScriptScene:
    index: int
    narration: str
    visual_direction: str
    on_screen_text: str = ""
    duration_hint_seconds: float = 6.0


@dataclass
class Script:
    title: str
    hook_line: str
    scenes: list[ScriptScene]
    call_to_action: str
    estimated_duration_seconds: float = 0.0

    def __post_init__(self) -> None:
        if not self.estimated_duration_seconds:
            self.estimated_duration_seconds = sum(
                s.duration_hint_seconds for s in self.scenes
            )


@dataclass
class MarketingPackage:
    title_options: list[str]
    chosen_title: str
    description: str
    tags: list[str]
    hashtags: list[str]
    thumbnail_concepts: list[str]


@dataclass
class ThumbnailAsset:
    path: str
    concept: str


@dataclass
class SceneAsset:
    scene_index: int
    image_path: str
    audio_path: str
    duration_seconds: float


@dataclass
class ProductionOutput:
    video_path: str
    scene_assets: list[SceneAsset]
    thumbnail: ThumbnailAsset


@dataclass
class PublishResult:
    published: bool
    video_id: str | None = None
    url: str | None = None
    reason: str | None = None


@dataclass
class PerformanceSnapshot:
    video_id: str
    captured_at: str
    views: int
    likes: int
    comments: int
    average_view_duration_seconds: float | None = None
    click_through_rate: float | None = None


@dataclass
class VideoProject:
    """The single unit of work that flows through every pipeline stage."""

    project_id: str
    niche: str
    created_at: str = field(default_factory=_now_iso)
    idea: VideoIdea | None = None
    research: ResearchBrief | None = None
    script: Script | None = None
    marketing: MarketingPackage | None = None
    production: ProductionOutput | None = None
    publish_result: PublishResult | None = None
    notes: list[str] = field(default_factory=list)

    def log(self, message: str) -> None:
        self.notes.append(f"[{_now_iso()}] {message}")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
