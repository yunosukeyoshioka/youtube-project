"""Persists each VideoProject's artifacts (metadata + generated files) to a
per-project directory under data/projects/<project_id>/."""

from __future__ import annotations

import json
import re
from pathlib import Path

from ..models import VideoProject


def slugify(text: str, max_length: int = 40) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return slug[:max_length] or "video"


class ProjectStore:
    def __init__(self, projects_dir: Path) -> None:
        self._projects_dir = Path(projects_dir)
        self._projects_dir.mkdir(parents=True, exist_ok=True)

    def project_dir(self, project_id: str) -> Path:
        path = self._projects_dir / project_id
        path.mkdir(parents=True, exist_ok=True)
        return path

    def scenes_dir(self, project_id: str) -> Path:
        path = self.project_dir(project_id) / "scenes"
        path.mkdir(parents=True, exist_ok=True)
        return path

    def save(self, project: VideoProject) -> Path:
        metadata_path = self.project_dir(project.project_id) / "project.json"
        with open(metadata_path, "w", encoding="utf-8") as fh:
            json.dump(project.to_dict(), fh, indent=2, ensure_ascii=False, default=str)
        return metadata_path

    def load(self, project_id: str) -> dict:
        metadata_path = self.project_dir(project_id) / "project.json"
        with open(metadata_path, encoding="utf-8") as fh:
            return json.load(fh)

    def list_project_ids(self) -> list[str]:
        if not self._projects_dir.exists():
            return []
        return sorted(
            p.name for p in self._projects_dir.iterdir() if (p / "project.json").exists()
        )
