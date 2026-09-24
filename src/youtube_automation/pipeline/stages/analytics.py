"""Stage 8: improvement. Pulls real performance numbers for previously
published videos and asks the LLM to distill actionable lessons, which are
stored in the knowledge base and injected into future ideation/marketing
prompts -- this is what makes the channel improve over time instead of
repeating the same mistakes."""

from __future__ import annotations

from ...providers.llm.base import LLMProvider
from ...providers.youtube.analytics import YouTubeStatsReader
from ...storage.knowledge_base import KnowledgeBase

SYSTEM_PROMPT = (
    "You are a YouTube channel growth analyst. Given performance data across "
    "several videos, extract concise, actionable lessons a scriptwriter and "
    "marketer can apply to future videos."
)


class ImprovementStage:
    def __init__(
        self,
        llm: LLMProvider,
        knowledge_base: KnowledgeBase,
        stats_reader: YouTubeStatsReader | None,
    ) -> None:
        self._llm = llm
        self._kb = knowledge_base
        self._stats_reader = stats_reader

    def refresh_performance(self) -> int:
        """Fetch current stats for every published video. Returns how many
        were updated. No-op (returns 0) if no stats reader is configured,
        e.g. in dry-run mode."""

        if self._stats_reader is None:
            return 0
        updated = 0
        for entry in self._kb.entries():
            video_id = entry.get("video_id")
            if not video_id:
                continue
            snapshot = self._stats_reader.fetch(video_id)
            self._kb.record_performance(entry["project_id"], snapshot)
            updated += 1
        return updated

    def derive_insights(self) -> list[str]:
        entries_with_performance = [e for e in self._kb.entries() if e.get("performance")]
        if not entries_with_performance:
            return []

        summary_lines = "\n".join(
            f"- {e['title']!r}: {e['performance']['views']} views, "
            f"{e['performance']['likes']} likes, tags={e.get('tags')}"
            for e in entries_with_performance
        )
        prompt = f"""Here is performance data for this channel's published videos:

{summary_lines}

Improve future videos: extract 3-6 specific, actionable insights about what
title styles, tags, or angles correlate with higher views for this channel.

Respond as JSON: {{"insights": ["..."]}}"""

        response = self._llm.generate_json(SYSTEM_PROMPT, prompt, max_tokens=3000)
        insights = list(response.get("insights", []))
        if insights:
            self._kb.add_insights(insights)
        return insights
