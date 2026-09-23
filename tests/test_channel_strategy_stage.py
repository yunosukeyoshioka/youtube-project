from youtube_automation.pipeline.stages.channel_strategy import ChannelStrategyStage
from youtube_automation.providers.llm.mock_provider import MockLLMProvider
from youtube_automation.providers.research.llm_knowledge_provider import (
    LLMKnowledgeResearchProvider,
)


def test_channel_strategy_proposes_distinct_concepts():
    stage = ChannelStrategyStage(MockLLMProvider(), LLMKnowledgeResearchProvider())

    concepts = stage.propose(interest_area="science facts", count=2, language="en")

    assert len(concepts) == 2
    names = {c.name for c in concepts}
    assert len(names) == 2  # concepts are distinct, not duplicates
    for concept in concepts:
        assert concept.niche
        assert concept.content_pillars
        assert concept.sample_video_titles
        assert concept.language == "en"
