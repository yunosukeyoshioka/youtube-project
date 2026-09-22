"""Assembles the final video with ffmpeg: each scene becomes a still-image
clip (Ken-Burns-free, simple and fast) with its narration audio and a burned
-in caption, then all scenes are concatenated.

Uses the `imageio-ffmpeg` package's bundled static ffmpeg binary so no system
package install is required. Captions are burned in via the `subtitles`
(libass) filter rather than `drawtext`, because several common static ffmpeg
builds (including the one imageio-ffmpeg bundles) ship without the drawtext
filter but do include libass.
"""

from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path

from ...models import SceneAsset
from .base import VideoAssembler


def _ffmpeg_binary() -> str:
    import imageio_ffmpeg

    return imageio_ffmpeg.get_ffmpeg_exe()


def _escape_for_filter(path: str) -> str:
    return path.replace("\\", "\\\\").replace(":", "\\:").replace("'", "\\'")


def _srt_timestamp(seconds: float) -> str:
    total_ms = max(0, round(seconds * 1000))
    hours, rem_ms = divmod(total_ms, 3_600_000)
    minutes, rem_ms = divmod(rem_ms, 60_000)
    secs, ms = divmod(rem_ms, 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{ms:03d}"


class FfmpegVideoAssembler(VideoAssembler):
    def __init__(self, fps: int = 30, resolution: str = "1280x720") -> None:
        self._fps = fps
        self._resolution = resolution
        self._ffmpeg = _ffmpeg_binary()

    def _render_scene_clip(
        self, scene: SceneAsset, caption: str, tmp_dir: Path, index: int
    ) -> Path:
        clip_path = tmp_dir / f"clip_{index:03d}.mp4"
        vf_parts = [f"scale={self._resolution.replace('x', ':')}"]

        if caption:
            srt_path = tmp_dir / f"caption_{index:03d}.srt"
            duration = max(scene.duration_seconds, 0.5)
            srt_path.write_text(
                f"1\n{_srt_timestamp(0)} --> {_srt_timestamp(duration)}\n{caption}\n",
                encoding="utf-8",
            )
            style = (
                "FontName=DejaVu Sans,FontSize=20,PrimaryColour=&H00FFFFFF,"
                "OutlineColour=&H00000000,BorderStyle=1,Outline=2,MarginV=40"
            )
            subtitles = (
                f"subtitles={_escape_for_filter(str(srt_path))}"
                f":force_style='{style}'"
            )
            vf_parts.append(subtitles)

        cmd = [
            self._ffmpeg,
            "-y",
            "-loop",
            "1",
            "-i",
            scene.image_path,
            "-i",
            scene.audio_path,
            "-vf",
            ",".join(vf_parts),
            "-c:v",
            "libx264",
            "-tune",
            "stillimage",
            "-c:a",
            "aac",
            "-b:a",
            "192k",
            "-pix_fmt",
            "yuv420p",
            "-r",
            str(self._fps),
            "-shortest",
            "-t",
            f"{max(scene.duration_seconds, 0.5):.2f}",
            str(clip_path),
        ]
        subprocess.run(cmd, check=True, capture_output=True)
        return clip_path

    def assemble(
        self,
        scene_assets: list[SceneAsset],
        scene_captions: list[str],
        output_path: str,
    ) -> str:
        if not scene_assets:
            raise ValueError("Cannot assemble a video with zero scenes.")

        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        with tempfile.TemporaryDirectory(prefix="ytauto_render_") as tmp:
            tmp_dir = Path(tmp)
            clip_paths = [
                self._render_scene_clip(scene, caption, tmp_dir, i)
                for i, (scene, caption) in enumerate(zip(scene_assets, scene_captions))
            ]

            concat_list = tmp_dir / "concat.txt"
            concat_list.write_text(
                "\n".join(f"file '{p.as_posix()}'" for p in clip_paths),
                encoding="utf-8",
            )

            cmd = [
                self._ffmpeg,
                "-y",
                "-f",
                "concat",
                "-safe",
                "0",
                "-i",
                str(concat_list),
                "-c",
                "copy",
                output_path,
            ]
            subprocess.run(cmd, check=True, capture_output=True)

        return output_path
