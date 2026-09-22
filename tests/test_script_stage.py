from youtube_automation.models import ResearchBrief, VideoIdea, VideoProject
from youtube_automation.pipeline.stages.script import ScriptStage
from youtube_automation.providers.llm.mock_provider import MockLLMProvider


def _project_with_idea_and_research() -> VideoProject:
    project = VideoProject(project_id="p1", niche="test")
    project.idea = VideoIdea(
        title="Some title",
        hook="hook",
        angle="angle",
        target_audience="aud",
        reasoning="reason",
        virality_score=5.0,
    )
    project.research = ResearchBrief(
        summary="summary", key_points=["a", "b"], sources=[]
    )
    return project


def test_script_stage_builds_scenes(offline_config):
    stage = ScriptStage(MockLLMProvider(), offline_config)
    project = _project_with_idea_and_research()

    stage.run(project)

    assert project.script is not None
    assert len(project.script.scenes) == 2
    assert project.script.estimated_duration_seconds > 0
    assert project.script.call_to_action
