from pathlib import Path

from youtube_automation.models import MarketingPackage, VideoProject
from youtube_automation.pipeline.stages.design import DesignStage
from youtube_automation.providers.image.local_provider import LocalImageProvider
from youtube_automation.storage.project_store import ProjectStore


def test_design_stage_renders_thumbnail(tmp_path: Path):
    store = ProjectStore(tmp_path / "projects")
    stage = DesignStage(LocalImageProvider(), store)

    project = VideoProject(project_id="p1", niche="test")
    project.marketing = MarketingPackage(
        title_options=["A Title"],
        chosen_title="A Title",
        description="desc",
        tags=["a"],
        hashtags=["#a"],
        thumbnail_concepts=["a dramatic concept"],
    )

    thumbnail = stage.run(project)

    assert Path(thumbnail.path).exists()
    assert Path(thumbnail.path).stat().st_size > 0
