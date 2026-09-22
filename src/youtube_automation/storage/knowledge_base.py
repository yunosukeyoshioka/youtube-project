"""A small JSON-backed knowledge base that closes the improvement loop: each
published video's idea/marketing choices and later performance numbers are
recorded here, and a summary of what worked is fed back into future
ideation/marketing prompts so the channel gets better over time."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from ..models import PerformanceSnapshot, VideoProject


class KnowledgeBase:
    def __init__(self, path: Path) -> None:
        self._path = Path(path)
        self._path.parent.mkdir(parents=True, exist_ok=True)
        if not self._path.exists():
            self._write({"entries": [], "insights": []})

    def _read(self) -> dict[str, Any]:
        with open(self._path, encoding="utf-8") as fh:
            return json.load(fh)

    def _write(self, data: dict[str, Any]) -> None:
        with open(self._path, "w", encoding="utf-8") as fh:
            json.dump(data, fh, indent=2, ensure_ascii=False, default=str)

    def record_project(self, project: VideoProject) -> None:
        data = self._read()
        entry = {
            "project_id": project.project_id,
            "niche": project.niche,
            "title": project.marketing.chosen_title if project.marketing else None,
            "virality_score": project.idea.virality_score if project.idea else None,
            "tags": project.marketing.tags if project.marketing else [],
            "video_id": project.publish_result.video_id
            if project.publish_result
            else None,
            "performance": None,
        }
        data["entries"] = [
            e for e in data["entries"] if e["project_id"] != project.project_id
        ]
        data["entries"].append(entry)
        self._write(data)

    def record_performance(self, project_id: str, snapshot: PerformanceSnapshot) -> None:
        data = self._read()
        for entry in data["entries"]:
            if entry["project_id"] == project_id:
                entry["performance"] = {
                    "views": snapshot.views,
                    "likes": snapshot.likes,
                    "comments": snapshot.comments,
                    "captured_at": snapshot.captured_at,
                }
        self._write(data)

    def add_insights(self, insights: list[str]) -> None:
        data = self._read()
        existing = set(data["insights"])
        for insight in insights:
            if insight not in existing:
                data["insights"].append(insight)
                existing.add(insight)
        self._write(data)

    def entries(self) -> list[dict[str, Any]]:
        return self._read()["entries"]

    def insights(self) -> list[str]:
        return self._read()["insights"]

    def best_performers(self, limit: int = 5) -> list[dict[str, Any]]:
        scored = [e for e in self.entries() if e.get("performance")]
        scored.sort(key=lambda e: e["performance"]["views"], reverse=True)
        return scored[:limit]

    def context_for_prompt(self) -> str:
        """A short text block to inject into ideation/marketing prompts so the
        LLM builds on what has actually worked for this channel before."""

        insights = self.insights()
        top = self.best_performers()
        if not insights and not top:
            return (
                "No performance history yet for this channel; use general best "
                "practices for high-retention YouTube videos."
            )
        lines = []
        if insights:
            lines.append("Lessons learned from past videos:")
            lines.extend(f"- {i}" for i in insights)
        if top:
            lines.append("Best-performing past titles (highest views first):")
            lines.extend(
                f"- {e['title']} ({e['performance']['views']} views)" for e in top
            )
        return "\n".join(lines)
