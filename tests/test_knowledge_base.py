from pathlib import Path

from youtube_automation.models import (
    MarketingPackage,
    PerformanceSnapshot,
    VideoIdea,
    VideoProject,
)
from youtube_automation.storage.knowledge_base import KnowledgeBase


def _project_with_marketing(project_id: str, title: str) -> VideoProject:
    project = VideoProject(project_id=project_id, niche="test")
    project.idea = VideoIdea(
        title=title,
        hook="h",
        angle="a",
        target_audience="t",
        reasoning="r",
        virality_score=7.0,
    )
    project.marketing = MarketingPackage(
        title_options=[title],
        chosen_title=title,
        description="d",
        tags=["tag"],
        hashtags=["#tag"],
        thumbnail_concepts=["c"],
    )
    return project


def test_knowledge_base_records_and_ranks_performance(tmp_path: Path):
    kb = KnowledgeBase(tmp_path / "kb.json")

    kb.record_project(_project_with_marketing("p1", "Low performer"))
    kb.record_project(_project_with_marketing("p2", "High performer"))

    kb.record_performance(
        "p1",
        PerformanceSnapshot(
            video_id="v1", captured_at="now", views=10, likes=1, comments=0
        ),
    )
    kb.record_performance(
        "p2",
        PerformanceSnapshot(
            video_id="v2", captured_at="now", views=1000, likes=50, comments=5
        ),
    )
    kb.add_insights(["Short titles win.", "Short titles win."])  # dedup check

    assert kb.insights() == ["Short titles win."]
    top = kb.best_performers(limit=1)
    assert top[0]["title"] == "High performer"

    prompt_context = kb.context_for_prompt()
    assert "High performer" in prompt_context
    assert "Short titles win." in prompt_context


def test_knowledge_base_empty_state_has_generic_guidance(tmp_path: Path):
    kb = KnowledgeBase(tmp_path / "kb.json")
    assert "general best practices" in kb.context_for_prompt()
