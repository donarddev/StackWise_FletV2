"""Learning Hub article repository."""

from __future__ import annotations

from typing import Optional

from app.models.learning_article import LearningArticle
from app.repositories.base_repository import BaseRepository


class LearningRepository(BaseRepository):
    def list_all(self) -> list[LearningArticle]:
        rows = self.db.fetch_all(
            "SELECT * FROM learning_articles ORDER BY category ASC, title ASC"
        )
        return [LearningArticle.from_row(r) for r in rows]

    def list_by_category(self, category: str) -> list[LearningArticle]:
        rows = self.db.fetch_all(
            "SELECT * FROM learning_articles WHERE category = %s ORDER BY title ASC",
            (category,),
        )
        return [LearningArticle.from_row(r) for r in rows]

    def list_categories(self) -> list[str]:
        rows = self.db.fetch_all(
            "SELECT DISTINCT category FROM learning_articles ORDER BY category ASC"
        )
        return [r["category"] for r in rows]

    def find_by_slug(self, slug: str) -> Optional[LearningArticle]:
        row = self.db.fetch_one(
            "SELECT * FROM learning_articles WHERE slug = %s LIMIT 1",
            (slug,),
        )
        return LearningArticle.from_row(row) if row else None

    def search(self, query: str) -> list[LearningArticle]:
        like = f"%{query.lower()}%"
        rows = self.db.fetch_all(
            "SELECT * FROM learning_articles "
            "WHERE LOWER(title) LIKE %s OR LOWER(summary) LIKE %s OR LOWER(tags) LIKE %s "
            "ORDER BY title ASC",
            (like, like, like),
        )
        return [LearningArticle.from_row(r) for r in rows]
