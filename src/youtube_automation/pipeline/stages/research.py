"""Stage 2: research. Gathers supporting facts/sources for the chosen idea
(via a web search provider when configured) and has the LLM synthesize them
into a structured brief the script writer can rely on."""

from __future__ import annotations

from ...models import ResearchBrief, VideoProject
from ...providers.llm.base import LLMProvider
from ...providers.research.base import ResearchProvider

SYSTEM_PROMPT = (
    "You are a meticulous research assistant preparing an accurate, well "
    "-sourced brief for a scriptwriter. Flag anything you are not confident "
    "about instead of inventing facts."
)


class ResearchStage:
    def __init__(self, llm: LLMProvider, research_provider: ResearchProvider) -> None:
        self._llm = llm
        self._research_provider = research_provider

    def run(self, project: VideoProject) -> None:
        assert project.idea is not None, "Ideation must run before research."
        search_results = self._research_provider.search(project.idea.title)

        sources_block = "\n".join(
            f"- {r.title} ({r.url}): {r.snippet}" for r in search_results
        ) or "No web search results available; rely on general knowledge and clearly flag it as unverified."

        prompt = f"""Prepare a research brief for a YouTube video.

Video title: {project.idea.title}
Angle: {project.idea.angle}
Target audience: {project.idea.target_audience}

Available sources:
{sources_block}

Respond as JSON: {{"summary": "...", "key_points": ["..."], "sources":
["..."], "open_questions": ["..."]}}"""

        response = self._llm.generate_json(SYSTEM_PROMPT, prompt, max_tokens=1500)
        project.research = ResearchBrief(
            summary=response.get("summary", ""),
            key_points=list(response.get("key_points", [])),
            sources=list(response.get("sources", [])) or [r.url for r in search_results],
            open_questions=list(response.get("open_questions", [])),
        )
        project.log(
            f"Research: gathered {len(project.research.key_points)} key points "
            f"from {len(search_results)} web sources."
        )
