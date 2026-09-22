"""Wires every stage together into the single "create a video" pipeline."""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime, timezone

from ..config import AppConfig, load_config
from ..models import VideoProject
from ..providers.image import build_image_provider
from ..providers.llm import build_llm_provider
from ..providers.research import build_research_provider
from ..providers.tts import build_tts_provider
from ..providers.video import build_video_assembler
from ..providers.youtube import YouTubeStatsReader, build_youtube_publisher
from ..storage import KnowledgeBase, ProjectStore
from .stages import (
    DesignStage,
    IdeationStage,
    ImprovementStage,
    MarketingStage,
    ProductionStage,
    PublishingStage,
    ResearchStage,
    ScriptStage,
)


@dataclass
class PipelineResult:
    project: VideoProject
    project_dir: str


class VideoPipeline:
    """Builds every provider/stage from config and runs the full create-a
    -video pipeline end to end."""

    def __init__(self, config: AppConfig | None = None) -> None:
        self.config = config or load_config()

        self.llm = build_llm_provider(self.config)
        self.research_provider = build_research_provider(self.config)
        self.tts_provider = build_tts_provider(self.config)
        self.image_provider = build_image_provider(self.config)
        self.video_assembler = build_video_assembler(self.config)
        self.publisher = build_youtube_publisher(self.config)

        self.project_store = ProjectStore(self.config.projects_dir)
        self.knowledge_base = KnowledgeBase(self.config.knowledge_base_path)

        self.stats_reader: YouTubeStatsReader | None = None
        if self.config.providers.youtube == "youtube_api":
            self.stats_reader = YouTubeStatsReader(
                self.config.youtube_client_secrets_file, self.config.youtube_token_file
            )

        self.ideation_stage = IdeationStage(self.llm, self.config, self.knowledge_base)
        self.research_stage = ResearchStage(self.llm, self.research_provider)
        self.script_stage = ScriptStage(self.llm, self.config)
        self.marketing_stage = MarketingStage(self.llm, self.knowledge_base)
        self.design_stage = DesignStage(self.image_provider, self.project_store)
        self.production_stage = ProductionStage(
            self.tts_provider, self.image_provider, self.video_assembler, self.project_store
        )
        self.publishing_stage = PublishingStage(
            self.publisher, privacy_status=self.config.raw.get("privacy_status", "private")
        )
        self.improvement_stage = ImprovementStage(
            self.llm, self.knowledge_base, self.stats_reader
        )

    def create_video(self, niche: str | None = None, publish: bool = True) -> PipelineResult:
        """Run the full pipeline: idea -> research -> script -> marketing ->
        design -> production -> (optionally) publish. Returns the finished
        VideoProject with every stage's output attached."""

        effective_niche = niche or self.config.channel.niche
        project = VideoProject(
            project_id=self._new_project_id(),
            niche=effective_niche,
        )
        project.log(f"Pipeline started for niche={effective_niche!r}.")

        self.ideation_stage.run(project)
        self.project_store.save(project)

        self.research_stage.run(project)
        self.project_store.save(project)

        self.script_stage.run(project)
        self.project_store.save(project)

        self.marketing_stage.run(project)
        self.project_store.save(project)

        thumbnail = self.design_stage.run(project)
        self.project_store.save(project)

        self.production_stage.run(project, thumbnail)
        self.project_store.save(project)

        if publish:
            self.publishing_stage.run(project)
        self.project_store.save(project)

        self.knowledge_base.record_project(project)
        project.log("Pipeline finished.")
        self.project_store.save(project)

        return PipelineResult(
            project=project, project_dir=str(self.project_store.project_dir(project.project_id))
        )

    def refresh_and_learn(self) -> list[str]:
        """Pull the latest performance numbers for published videos and
        derive fresh insights for future runs. Safe to call anytime; it's a
        no-op if nothing has been published with real YouTube credentials
        yet."""

        self.improvement_stage.refresh_performance()
        return self.improvement_stage.derive_insights()

    @staticmethod
    def _new_project_id() -> str:
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
        return f"{timestamp}-{uuid.uuid4().hex[:6]}"
