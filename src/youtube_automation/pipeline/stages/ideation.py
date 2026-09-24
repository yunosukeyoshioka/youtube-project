"""Stage 1: idea generation. Brainstorms several video concepts for the
channel's niche, informed by what has worked before, and picks the one with
the highest estimated virality score."""

from __future__ import annotations

from ...config import AppConfig
from ...models import VideoIdea, VideoProject
from ...providers.llm.base import LLMProvider
from ...storage.knowledge_base import KnowledgeBase

SYSTEM_PROMPT = (
    "You are an expert YouTube content strategist who studies trending videos, "
    "audience retention data, and click-through psychology to consistently "
    "produce high-performing video ideas."
)


class IdeationStage:
    def __init__(
        self, llm: LLMProvider, config: AppConfig, knowledge_base: KnowledgeBase
    ) -> None:
        self._llm = llm
        self._config = config
        self._kb = knowledge_base

    def run(self, project: VideoProject) -> None:
        channel = self._config.channel
        prompt = f"""Brainstorm 5 YouTube video ideas for this channel.

Channel niche: {channel.niche}
Target audience: {channel.audience}
Tone: {channel.tone}
Target video length: ~{channel.video_length_seconds} seconds

{self._kb.context_for_prompt()}

For each idea, provide: title (curiosity-driven, under 70 characters), hook
(the first line that stops someone scrolling), angle (why this take is
different), target_audience, reasoning (why this will get views), a
virality_score from 0-10, and 3-5 tags.

Respond as JSON: {{"ideas": [{{"title": "...", "hook": "...", "angle": "...",
"target_audience": "...", "reasoning": "...", "virality_score": 0.0,
"tags": ["..."]}}]}}"""

        response = self._llm.generate_json(SYSTEM_PROMPT, prompt, max_tokens=4000)
        ideas_raw = response.get("ideas", [])
        if not ideas_raw:
            raise RuntimeError("Ideation stage received no ideas from the LLM provider.")

        ideas = [
            VideoIdea(
                title=i["title"],
                hook=i["hook"],
                angle=i.get("angle", ""),
                target_audience=i.get("target_audience", channel.audience),
                reasoning=i.get("reasoning", ""),
                virality_score=float(i.get("virality_score", 0)),
                tags=list(i.get("tags", [])),
            )
            for i in ideas_raw
        ]
        best = max(ideas, key=lambda idea: idea.virality_score)
        project.idea = best
        project.log(
            f"Ideation: selected {best.title!r} (score={best.virality_score}) "
            f"out of {len(ideas)} candidates."
        )
