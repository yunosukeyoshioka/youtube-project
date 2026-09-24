"""Channel strategist: analyzes the current competitive landscape (real
subscriber/view counts when the YouTube Data API research provider is
configured, otherwise the LLM's general knowledge) and proposes distinct new
channel concepts -- name, niche, target audience, tone, and positioning --
each ready to be saved as its own channel config and run independently."""

from __future__ import annotations

from ...models import ChannelConcept
from ...providers.llm.base import LLMProvider
from ...providers.research.base import ResearchProvider

SYSTEM_PROMPT = (
    "You are a YouTube channel strategist who studies the competitive "
    "landscape (subscriber counts, view counts, currently popular titles) "
    "and designs new channel concepts positioned to stand out and grow, "
    "not just copy what already exists."
)


class ChannelStrategyStage:
    def __init__(self, llm: LLMProvider, research_provider: ResearchProvider) -> None:
        self._llm = llm
        self._research_provider = research_provider

    def propose(
        self,
        interest_area: str,
        count: int = 3,
        language: str = "en",
        video_length_seconds: int = 90,
    ) -> list[ChannelConcept]:
        landscape = self._research_provider.search(
            f"popular YouTube channels and videos: {interest_area}", max_results=10
        )
        landscape_block = "\n".join(
            f"- {r.title} ({r.url}): {r.snippet}" for r in landscape
        ) or (
            "No live competitor data available; rely on general knowledge of "
            "what tends to perform well on YouTube and flag it as unverified."
        )

        prompt = f"""Propose {count} distinct YouTube channel concepts for this
interest area: {interest_area!r}

Current competitive landscape:
{landscape_block}

For each channel concept, provide: name (catchy, memorable, under 40
characters), niche (specific content focus, not generic), audience (who
exactly this is for), tone (how the channel sounds/feels), positioning (how
it differs from the channels/videos above -- the gap it fills),
content_pillars (3-5 recurring content themes/series this channel would
produce), sample_video_titles (3 concrete first-video title ideas), and
reasoning (why this concept can grow given the landscape above).

Make the {count} concepts meaningfully different from each other, not
variations on the same idea.

Respond as JSON: {{"concepts": [{{"name": "...", "niche": "...",
"audience": "...", "tone": "...", "positioning": "...",
"content_pillars": ["..."], "sample_video_titles": ["..."],
"reasoning": "..."}}]}}"""

        response = self._llm.generate_json(SYSTEM_PROMPT, prompt, max_tokens=6000)
        concepts_raw = response.get("concepts", [])
        if not concepts_raw:
            raise RuntimeError("Channel strategy stage received no concepts from the LLM provider.")

        return [
            ChannelConcept(
                name=c["name"],
                niche=c["niche"],
                audience=c.get("audience", ""),
                tone=c.get("tone", ""),
                positioning=c.get("positioning", ""),
                content_pillars=list(c.get("content_pillars", [])),
                sample_video_titles=list(c.get("sample_video_titles", [])),
                reasoning=c.get("reasoning", ""),
                language=language,
                video_length_seconds=video_length_seconds,
            )
            for c in concepts_raw
        ]
