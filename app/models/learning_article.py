"""Learning Hub article entity."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Mapping

from app.helpers.date_helper import from_db


@dataclass
class LearningArticle:
    id: int
    slug: str
    category: str
    title: str
    summary: str
    content: str
    tags: list[str]
    created_at: datetime

    @staticmethod
    def from_row(row: Mapping[str, Any]) -> "LearningArticle":
        tags_csv: str = row["tags"] or ""
        return LearningArticle(
            id=int(row["id"]),
            slug=row["slug"],
            category=row["category"],
            title=row["title"],
            summary=row["summary"],
            content=row["content"],
            tags=[t.strip() for t in tags_csv.split(",") if t.strip()],
            created_at=from_db(row["created_at"]),
        )
