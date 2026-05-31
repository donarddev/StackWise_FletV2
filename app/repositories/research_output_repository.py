"""Repository for research support output persistence."""

from __future__ import annotations

from typing import Any, Optional

from app.models.research_output_model import ResearchOutput
from app.repositories.base_repository import BaseRepository
from app.utils.logger import get_logger

log = get_logger(__name__)


class ResearchOutputRepository(BaseRepository):
    def create_table_if_not_exists(self) -> dict[str, Any]:
        try:
            self.db.script(
                """
                CREATE TABLE IF NOT EXISTS research_outputs (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    recommendation_id INT NOT NULL,
                    user_id INT NULL,
                    research_type VARCHAR(100) NULL,
                    research_title VARCHAR(255) NULL,
                    research_inputs_json LONGTEXT NULL,
                    research_draft_json LONGTEXT NULL,
                    suggested_journals_json LONGTEXT NULL,
                    search_queries_json LONGTEXT NULL,
                    open_access_links_json LONGTEXT NULL,
                    publication_recommendation_json LONGTEXT NULL,
                    scopus_verification_note TEXT NULL,
                    generated_by_model VARCHAR(100) NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    INDEX idx_research_recommendation (recommendation_id),
                    INDEX idx_research_user (user_id)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
                """
            )
            return {"success": True, "data": {"table": "research_outputs"}}
        except Exception as exc:
            log.exception("Failed creating research_outputs table")
            return {"success": False, "error": str(exc)}

    def save_or_update_research_output(
        self,
        recommendation_id: int,
        user_id: Optional[int],
        research_output_data: dict[str, Any],
    ) -> dict[str, Any]:
        try:
            ready = self.create_table_if_not_exists()
            if not ready.get("success"):
                return ready

            current_row = self._find_existing_row(recommendation_id, user_id)
            payload = self._row_payload(recommendation_id, user_id, research_output_data)

            if current_row:
                self.db.execute(
                    """
                    UPDATE research_outputs
                    SET
                        research_type = %s,
                        research_title = %s,
                        research_inputs_json = %s,
                        research_draft_json = %s,
                        suggested_journals_json = %s,
                        search_queries_json = %s,
                        open_access_links_json = %s,
                        publication_recommendation_json = %s,
                        scopus_verification_note = %s,
                        generated_by_model = %s
                    WHERE id = %s
                    """,
                    (
                        payload["research_type"],
                        payload["research_title"],
                        payload["research_inputs_json"],
                        payload["research_draft_json"],
                        payload["suggested_journals_json"],
                        payload["search_queries_json"],
                        payload["open_access_links_json"],
                        payload["publication_recommendation_json"],
                        payload["scopus_verification_note"],
                        payload["generated_by_model"],
                        int(current_row["id"]),
                    ),
                )
                output_id = int(current_row["id"])
            else:
                output_id = self.db.execute(
                    """
                    INSERT INTO research_outputs (
                        recommendation_id,
                        user_id,
                        research_type,
                        research_title,
                        research_inputs_json,
                        research_draft_json,
                        suggested_journals_json,
                        search_queries_json,
                        open_access_links_json,
                        publication_recommendation_json,
                        scopus_verification_note,
                        generated_by_model
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        recommendation_id,
                        user_id,
                        payload["research_type"],
                        payload["research_title"],
                        payload["research_inputs_json"],
                        payload["research_draft_json"],
                        payload["suggested_journals_json"],
                        payload["search_queries_json"],
                        payload["open_access_links_json"],
                        payload["publication_recommendation_json"],
                        payload["scopus_verification_note"],
                        payload["generated_by_model"],
                    ),
                )

            row = self.db.fetch_one(
                "SELECT * FROM research_outputs WHERE id = %s LIMIT 1",
                (output_id,),
            )
            model = ResearchOutput.from_db_row_optional(row)
            return {"success": True, "data": model.to_dict() if model else None}
        except Exception as exc:
            log.exception(
                "save_or_update_research_output failed recommendation_id=%s user_id=%s",
                recommendation_id,
                user_id,
            )
            return {"success": False, "error": str(exc)}

    def get_by_recommendation_id(
        self,
        recommendation_id: int,
        user_id: Optional[int] = None,
    ) -> dict[str, Any]:
        try:
            row = self._find_existing_row(recommendation_id, user_id)
            if not row:
                return {"success": True, "data": None}
            model = ResearchOutput.from_db_row(row)
            return {"success": True, "data": model.to_dict()}
        except Exception as exc:
            log.exception(
                "get_by_recommendation_id failed recommendation_id=%s user_id=%s",
                recommendation_id,
                user_id,
            )
            return {"success": False, "error": str(exc)}

    def delete_by_recommendation_id(
        self,
        recommendation_id: int,
        user_id: Optional[int] = None,
    ) -> dict[str, Any]:
        try:
            row = self._find_existing_row(recommendation_id, user_id)
            if not row:
                return {"success": True, "data": {"deleted": False, "reason": "not_found"}}

            self.db.execute(
                "DELETE FROM research_outputs WHERE id = %s",
                (int(row["id"]),),
            )
            return {"success": True, "data": {"deleted": True}}
        except Exception as exc:
            log.exception(
                "delete_by_recommendation_id failed recommendation_id=%s user_id=%s",
                recommendation_id,
                user_id,
            )
            return {"success": False, "error": str(exc)}

    def has_research_output(
        self,
        recommendation_id: int,
        user_id: Optional[int] = None,
    ) -> dict[str, Any]:
        try:
            row = self._find_existing_row(recommendation_id, user_id)
            return {"success": True, "data": bool(row)}
        except Exception as exc:
            log.exception(
                "has_research_output failed recommendation_id=%s user_id=%s",
                recommendation_id,
                user_id,
            )
            return {"success": False, "error": str(exc)}

    def _find_existing_row(self, recommendation_id: int, user_id: Optional[int]) -> dict[str, Any] | None:
        if user_id is None:
            return self.db.fetch_one(
                """
                SELECT * FROM research_outputs
                WHERE recommendation_id = %s
                ORDER BY id DESC
                LIMIT 1
                """,
                (recommendation_id,),
            )

        return self.db.fetch_one(
            """
            SELECT * FROM research_outputs
            WHERE recommendation_id = %s AND user_id = %s
            ORDER BY id DESC
            LIMIT 1
            """,
            (recommendation_id, user_id),
        )

    def _row_payload(
        self,
        recommendation_id: int,
        user_id: Optional[int],
        data: dict[str, Any],
    ) -> dict[str, Any]:
        _ = recommendation_id, user_id
        return {
            "research_type": str(data.get("research_type") or ""),
            "research_title": str(data.get("research_title") or ""),
            "research_inputs_json": ResearchOutput.dict_to_json(data.get("research_inputs") or {}),
            "research_draft_json": ResearchOutput.dict_to_json(data.get("research_draft") or {}),
            "suggested_journals_json": ResearchOutput.dict_to_json(data.get("suggested_journals") or []),
            "search_queries_json": ResearchOutput.dict_to_json(data.get("search_queries") or []),
            "open_access_links_json": ResearchOutput.dict_to_json(data.get("open_access_links") or []),
            "publication_recommendation_json": ResearchOutput.dict_to_json(
                data.get("publication_recommendation") or {},
            ),
            "scopus_verification_note": str(data.get("scopus_verification_note") or ""),
            "generated_by_model": str(data.get("generated_by_model") or "dummy-local-template"),
        }
