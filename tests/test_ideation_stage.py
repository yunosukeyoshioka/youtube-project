from pathlib import Path

from youtube_automation.models import VideoProject
from youtube_automation.pipeline.stages.ideation import IdeationStage
from youtube_automation.providers.llm.mock_provider import MockLLMProvider
from youtube_automation.storage.knowledge_base import KnowledgeBase


def test_ideation_picks_highest_virality_idea(offline_config, tmp_path: Path):
    llm = MockLLMProvider(
        canned_responses={
            "brainstorm": {
                "ideas": [
                    {
                        "title": "Low score idea",
                        "hook": "h1",
                        "angle": "a1",
                        "target_audience": "t1",
                        "reasoning": "r1",
                        "virality_score": 3.0,
                        "tags": ["x"],
                    },
                    {
                        "title": "High score idea",
                        "hook": "h2",
                        "angle": "a2",
                        "target_audience": "t2",
                        "reasoning": "r2",
                        "virality_score": 9.5,
                        "tags": ["y"],
                    },
                ]
            }
        }
    )
    kb = KnowledgeBase(tmp_path / "kb.json")
    stage = IdeationStage(llm, offline_config, kb)
    project = VideoProject(project_id="p1", niche="test")

    stage.run(project)

    assert project.idea is not None
    assert project.idea.title == "High score idea"
    assert project.notes  # logged something
