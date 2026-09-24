"""Stage 4: marketing. Generates SEO-optimized titles, description, tags,
hashtags, and thumbnail concepts from the finished script."""

from __future__ import annotations

from ...models import MarketingPackage, VideoProject
from ...providers.llm.base import LLMProvider
from ...storage.knowledge_base import KnowledgeBase

SYSTEM_PROMPT = (
    "You are a YouTube SEO and marketing specialist who optimizes titles, "
    "descriptions, and thumbnail concepts for maximum click-through rate and "
    "search discoverability without resorting to misleading clickbait."
)


class MarketingStage:
    def __init__(self, llm: LLMProvider, knowledge_base: KnowledgeBase) -> None:
        self._llm = llm
        self._kb = knowledge_base

    def run(self, project: VideoProject) -> None:
        assert project.script is not None, "Script must run before marketing."
        assert project.idea is not None

        prompt = f"""Create a marketing package for this YouTube video.

Working title: {project.script.title}
Hook line: {project.script.hook_line}
Scene summaries: {"; ".join(s.narration for s in project.script.scenes)}
Tags from ideation: {", ".join(project.idea.tags)}

{self._kb.context_for_prompt()}

Provide: title_options (5 alternative titles under 70 characters, ranked
best first), chosen_title (your top pick), description (150-300 words,
SEO-friendly, include a natural call to action), tags (10-15 search tags),
hashtags (3-5), and thumbnail_concepts (2-3 short visual descriptions for a
high-CTR thumbnail).

Respond as JSON: {{"title_options": ["..."], "chosen_title": "...",
"description": "...", "tags": ["..."], "hashtags": ["..."],
"thumbnail_concepts": ["..."]}}"""

        response = self._llm.generate_json(SYSTEM_PROMPT, prompt, max_tokens=4000)
        project.marketing = MarketingPackage(
            title_options=list(response.get("title_options", [project.script.title])),
            chosen_title=response.get("chosen_title", project.script.title),
            description=response.get("description", ""),
            tags=list(response.get("tags", [])),
            hashtags=list(response.get("hashtags", [])),
            thumbnail_concepts=list(response.get("thumbnail_concepts", [])),
        )
        project.log(f"Marketing: chosen title {project.marketing.chosen_title!r}.")
