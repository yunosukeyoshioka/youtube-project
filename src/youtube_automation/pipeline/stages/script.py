"""Stage 3: script writing. Turns the idea + research brief into a
scene-by-scene narration script sized to the channel's target length."""

from __future__ import annotations

from ...config import AppConfig
from ...models import Script, ScriptScene, VideoProject
from ...providers.llm.base import LLMProvider

SYSTEM_PROMPT = (
    "You are an expert YouTube scriptwriter known for high-retention hooks, "
    "tight pacing, and scripts that are easy to narrate and illustrate scene "
    "by scene."
)


class ScriptStage:
    def __init__(self, llm: LLMProvider, config: AppConfig) -> None:
        self._llm = llm
        self._config = config

    def run(self, project: VideoProject) -> None:
        assert project.idea is not None, "Ideation must run before scripting."
        assert project.research is not None, "Research must run before scripting."
        channel = self._config.channel
        target_scenes = max(3, round(channel.video_length_seconds / 8))

        prompt = f"""Write a YouTube video script.

Title: {project.idea.title}
Hook: {project.idea.hook}
Tone: {channel.tone}
Target length: ~{channel.video_length_seconds} seconds ({target_scenes} scenes)

Research summary: {project.research.summary}
Key points to cover: {"; ".join(project.research.key_points)}

Write a hook_line (first spoken line, must grab attention in under 3
seconds) and {target_scenes} scenes. Each scene needs: narration (what's
spoken, 1-3 sentences), visual_direction (what should be shown on screen),
on_screen_text (a short caption/label overlay, under 6 words), and
duration_hint_seconds (realistic for the narration length). End with a
call_to_action.

Respond as JSON: {{"hook_line": "...", "scenes": [{{"narration": "...",
"visual_direction": "...", "on_screen_text": "...",
"duration_hint_seconds": 0}}], "call_to_action": "..."}}"""

        response = self._llm.generate_json(SYSTEM_PROMPT, prompt, max_tokens=3000)
        scenes = [
            ScriptScene(
                index=i,
                narration=s["narration"],
                visual_direction=s.get("visual_direction", ""),
                on_screen_text=s.get("on_screen_text", ""),
                duration_hint_seconds=float(s.get("duration_hint_seconds", 6.0)),
            )
            for i, s in enumerate(response.get("scenes", []))
        ]
        if not scenes:
            raise RuntimeError("Script stage received no scenes from the LLM provider.")

        project.script = Script(
            title=project.idea.title,
            hook_line=response.get("hook_line", project.idea.hook),
            scenes=scenes,
            call_to_action=response.get(
                "call_to_action", "Subscribe for more videos like this."
            ),
        )
        project.log(
            f"Script: wrote {len(scenes)} scenes, "
            f"~{project.script.estimated_duration_seconds:.0f}s estimated runtime."
        )
