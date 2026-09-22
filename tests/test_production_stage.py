from pathlib import Path

from youtube_automation.models import Script, ScriptScene, ThumbnailAsset, VideoProject
from youtube_automation.pipeline.stages.production import ProductionStage
from youtube_automation.providers.image.local_provider import LocalImageProvider
from youtube_automation.providers.tts.silent_provider import SilentPlaceholderTTSProvider
from youtube_automation.providers.video.ffmpeg_assembler import FfmpegVideoAssembler
from youtube_automation.storage.project_store import ProjectStore


def test_production_stage_renders_real_video_file(tmp_path: Path):
    """End-to-end (no mocks) check that TTS + image + ffmpeg actually produce
    a playable video file, proving the pipeline isn't just wired together on
    paper."""

    store = ProjectStore(tmp_path / "projects")
    stage = ProductionStage(
        SilentPlaceholderTTSProvider(),
        LocalImageProvider(),
        FfmpegVideoAssembler(),
        store,
    )

    project = VideoProject(project_id="p1", niche="test")
    project.script = Script(
        title="Test Video",
        hook_line="hook",
        scenes=[
            ScriptScene(
                index=0,
                narration="This is the first scene of the test video.",
                visual_direction="a title card",
                on_screen_text="Scene One",
            ),
            ScriptScene(
                index=1,
                narration="This is the second scene wrapping things up.",
                visual_direction="a closing card",
                on_screen_text="Scene Two",
            ),
        ],
        call_to_action="subscribe",
    )
    thumbnail = ThumbnailAsset(path=str(tmp_path / "thumb.png"), concept="c")

    stage.run(project, thumbnail)

    assert project.production is not None
    video_path = Path(project.production.video_path)
    assert video_path.exists()
    assert video_path.stat().st_size > 1000  # a real (if tiny) mp4, not an empty file
    assert len(project.production.scene_assets) == 2
    for scene_asset in project.production.scene_assets:
        assert Path(scene_asset.image_path).exists()
        assert Path(scene_asset.audio_path).exists()
        assert scene_asset.duration_seconds > 0
