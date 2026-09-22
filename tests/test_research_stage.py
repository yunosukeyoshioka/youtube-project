from youtube_automation.models import VideoIdea, VideoProject
from youtube_automation.pipeline.stages.research import ResearchStage
from youtube_automation.providers.llm.mock_provider import MockLLMProvider
from youtube_automation.providers.research.llm_knowledge_provider import (
    LLMKnowledgeResearchProvider,
)


def test_research_stage_falls_back_to_llm_knowledge():
    stage = ResearchStage(MockLLMProvider(), LLMKnowledgeResearchProvider())
    project = VideoProject(project_id="p1", niche="test")
    project.idea = VideoIdea(
        title="Some title",
        hook="hook",
        angle="angle",
        target_audience="aud",
        reasoning="reason",
        virality_score=5.0,
    )

    stage.run(project)

    assert project.research is not None
    assert project.research.key_points
