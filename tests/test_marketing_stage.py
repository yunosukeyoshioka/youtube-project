from pathlib import Path

from youtube_automation.models import Script, ScriptScene, VideoIdea, VideoProject
from youtube_automation.pipeline.stages.marketing import MarketingStage
from youtube_automation.providers.llm.mock_provider import MockLLMProvider
from youtube_automation.storage.knowledge_base import KnowledgeBase


def test_marketing_stage_builds_package(tmp_path: Path):
    kb = KnowledgeBase(tmp_path / "kb.json")
    stage = MarketingStage(MockLLMProvider(), kb)

    project = VideoProject(project_id="p1", niche="test")
    project.idea = VideoIdea(
        title="Some title",
        hook="hook",
        angle="angle",
        target_audience="aud",
        reasoning="reason",
        virality_score=5.0,
        tags=["a", "b"],
    )
    project.script = Script(
        title="Some title",
        hook_line="hook",
        scenes=[ScriptScene(index=0, narration="n", visual_direction="v")],
        call_to_action="subscribe",
    )

    stage.run(project)

    assert project.marketing is not None
    assert project.marketing.chosen_title
    assert project.marketing.tags
