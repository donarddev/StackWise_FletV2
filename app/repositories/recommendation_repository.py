"""Recommendation repository.

Owns persistence of recommendations and the recommendation_history audit
table. Returns rich entities; emits no domain logic.
"""

from __future__ import annotations

import json
from typing import Optional

from app.models.recommendation import Recommendation
from app.repositories.base_repository import BaseRepository


class RecommendationRepository(BaseRepository):
    # ---------- recommendations ----------

    def create(
        self,
        user_id: int,
        request: dict,
        result: dict,
    ) -> Recommendation:
        new_id = self.db.execute(
            """
            INSERT INTO recommendations (
                user_id, project_name, project_type, project_goal,
                complexity, team_size, timeline, scalability, security,
                platform, experience,
                recommended_language, recommended_framework, recommended_sdlc,
                confidence_score, explanation_json, alternatives_json, project_profile_json
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                user_id,
                request["project_name"],
                request["project_type"],
                request["project_goal"][:80],
                request["complexity"],
                request["team_size"],
                request["timeline"],
                request["scalability_needs"],
                request["security_requirements"],
                request["preferred_platform"],
                request["development_experience"],
                result["recommended_language"],
                result["recommended_framework"],
                result["recommended_sdlc"],
                int(result["confidence_score"]),
                json.dumps(result.get("explanation", {}), ensure_ascii=False),
                json.dumps(result.get("alternatives", {}), ensure_ascii=False),
                json.dumps(request, ensure_ascii=False),
            ),
        )
        self.add_history(user_id, new_id, "created")
        return self.find_by_id(new_id)  # type: ignore[return-value]

    def find_by_id(self, rec_id: int) -> Optional[Recommendation]:
        row = self.db.fetch_one(
            "SELECT * FROM recommendations WHERE id = %s LIMIT 1",
            (rec_id,),
        )
        return Recommendation.from_row_optional(row)

    def list_active_for_user(self, user_id: int, limit: int = 100) -> list[Recommendation]:
        rows = self.db.fetch_all(
            "SELECT * FROM recommendations WHERE user_id = %s AND deleted_at IS NULL "
            "ORDER BY created_at DESC LIMIT %s",
            (user_id, int(limit)),
        )
        return [Recommendation.from_row(r) for r in rows]

    def list_deleted_for_user(self, user_id: int, limit: int = 100) -> list[Recommendation]:
        rows = self.db.fetch_all(
            "SELECT * FROM recommendations WHERE user_id = %s AND deleted_at IS NOT NULL "
            "ORDER BY deleted_at DESC LIMIT %s",
            (user_id, int(limit)),
        )
        return [Recommendation.from_row(r) for r in rows]

    def list_for_user(self, user_id: int, limit: int = 100) -> list[Recommendation]:
        """Active recommendations only (excludes soft-deleted rows)."""
        return self.list_active_for_user(user_id, limit=limit)

    def latest_for_user(self, user_id: int, limit: int = 5) -> list[Recommendation]:
        return self.list_active_for_user(user_id, limit=limit)

    def count_for_user(self, user_id: int) -> int:
        row = self.db.fetch_one(
            "SELECT COUNT(*) AS c FROM recommendations "
            "WHERE user_id = %s AND deleted_at IS NULL",
            (user_id,),
        )
        return int(row["c"]) if row else 0

    def average_confidence(self, user_id: int) -> float:
        row = self.db.fetch_one(
            "SELECT AVG(confidence_score) AS avg_score "
            "FROM recommendations WHERE user_id = %s AND deleted_at IS NULL",
            (user_id,),
        )
        return float((row or {}).get("avg_score") or 0.0)

    def top_languages(self, user_id: int, limit: int = 5) -> list[tuple[str, int]]:
        rows = self.db.fetch_all(
            """
            SELECT recommended_language AS name, COUNT(*) AS c
            FROM recommendations WHERE user_id = %s AND deleted_at IS NULL
            GROUP BY recommended_language
            ORDER BY c DESC, name ASC LIMIT %s
            """,
            (user_id, int(limit)),
        )
        return [(r["name"], int(r["c"])) for r in rows]

    def top_frameworks(self, user_id: int, limit: int = 5) -> list[tuple[str, int]]:
        rows = self.db.fetch_all(
            """
            SELECT recommended_framework AS name, COUNT(*) AS c
            FROM recommendations WHERE user_id = %s AND deleted_at IS NULL
            GROUP BY recommended_framework
            ORDER BY c DESC, name ASC LIMIT %s
            """,
            (user_id, int(limit)),
        )
        return [(r["name"], int(r["c"])) for r in rows]

    def top_sdlc(self, user_id: int, limit: int = 5) -> list[tuple[str, int]]:
        rows = self.db.fetch_all(
            """
            SELECT recommended_sdlc AS name, COUNT(*) AS c
            FROM recommendations WHERE user_id = %s AND deleted_at IS NULL
            GROUP BY recommended_sdlc
            ORDER BY c DESC, name ASC LIMIT %s
            """,
            (user_id, int(limit)),
        )
        return [(r["name"], int(r["c"])) for r in rows]

    def trend_by_week(self, user_id: int, weeks: int = 8) -> list[tuple[str, int]]:
        """Return a list of (year-week-label, count) ordered oldest→newest.

        Uses MySQL's ``DATE_FORMAT`` (``%%`` is escaped because PyMySQL also
        uses ``%`` as its parameter placeholder marker).
        """
        rows = self.db.fetch_all(
            """
            SELECT DATE_FORMAT(created_at, '%%Y-%%u') AS bucket, COUNT(*) AS c
            FROM recommendations WHERE user_id = %s AND deleted_at IS NULL
            GROUP BY bucket
            ORDER BY bucket DESC LIMIT %s
            """,
            (user_id, int(weeks)),
        )
        return list(reversed([(r["bucket"], int(r["c"])) for r in rows]))

    # ---------- history audit ----------

    def add_history(self, user_id: int, recommendation_id: int, action: str) -> None:
        self.db.execute(
            "INSERT INTO recommendation_history (user_id, recommendation_id, action) "
            "VALUES (%s, %s, %s)",
            (user_id, recommendation_id, action),
        )

    def soft_delete(self, rec_id: int, user_id: int) -> bool:
        """Mark a recommendation as deleted (does not remove the row)."""
        self.db.execute(
            """
            UPDATE recommendations
            SET deleted_at = CURRENT_TIMESTAMP
            WHERE id = %s AND user_id = %s AND deleted_at IS NULL
            """,
            (rec_id, user_id),
        )
        row = self.db.fetch_one(
            "SELECT id FROM recommendations "
            "WHERE id = %s AND user_id = %s AND deleted_at IS NOT NULL LIMIT 1",
            (rec_id, user_id),
        )
        return row is not None

    def restore(self, rec_id: int, user_id: int) -> bool:
        """Clear deleted_at so the recommendation appears in History/Dashboard again."""
        self.db.execute(
            """
            UPDATE recommendations
            SET deleted_at = NULL
            WHERE id = %s AND user_id = %s AND deleted_at IS NOT NULL
            """,
            (rec_id, user_id),
        )
        row = self.db.fetch_one(
            "SELECT id FROM recommendations "
            "WHERE id = %s AND user_id = %s AND deleted_at IS NULL LIMIT 1",
            (rec_id, user_id),
        )
        return row is not None

    def delete(self, rec_id: int, user_id: int) -> None:
        """Legacy hard delete — prefer soft_delete."""
        self.db.execute(
            "DELETE FROM recommendations WHERE id = %s AND user_id = %s",
            (rec_id, user_id),
        )
