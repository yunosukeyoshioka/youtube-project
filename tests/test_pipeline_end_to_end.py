from pathlib import Path

from youtube_automation.config import AppConfig
from youtube_automation.pipeline.orchestrator import VideoPipeline


def test_full_pipeline_runs_offline_and_produces_a_video(offline_config: AppConfig):
    """The whole point of this project: one call produces a real (if
    placeholder-quality) video end to end, with zero network access and zero
    paid API keys, using the mock LLM + local/offline providers."""

    pipeline = VideoPipeline(offline_config)

    result = pipeline.create_video(niche="unit testing", publish=True)
    project = result.project

    assert project.idea is not None
    assert project.research is not None
    assert project.script is not None
    assert project.marketing is not None
    assert project.production is not None

    video_path = Path(project.production.video_path)
    assert video_path.exists() and video_path.stat().st_size > 1000

    thumbnail_path = Path(project.production.thumbnail.path)
    assert thumbnail_path.exists() and thumbnail_path.stat().st_size > 0

    # dry-run provider: rendered but not actually uploaded
    assert project.publish_result is not None
    assert project.publish_result.published is False

    # persisted to disk and recorded in the knowledge base
    saved = pipeline.project_store.load(project.project_id)
    assert saved["marketing"]["chosen_title"] == project.marketing.chosen_title

    kb_entries = pipeline.knowledge_base.entries()
    assert any(e["project_id"] == project.project_id for e in kb_entries)


def test_refresh_and_learn_is_a_safe_noop_without_youtube_credentials(
    offline_config: AppConfig,
):
    pipeline = VideoPipeline(offline_config)
    pipeline.create_video(niche="unit testing", publish=True)

    insights = pipeline.refresh_and_learn()

    # no video_id was ever published (dry-run), so there's nothing to learn from yet
    assert insights == []
