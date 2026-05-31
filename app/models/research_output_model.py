"""Research output entity model."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Mapping, Optional

from app.helpers.date_helper import from_db


@dataclass
class ResearchOutput:
    id: int = 0
    recommendation_id: int = 0
    user_id: Optional[int] = None
    research_type: str = ""
    research_title: str = ""
    research_inputs: dict[str, Any] = field(default_factory=dict)
    research_draft: dict[str, Any] = field(default_factory=dict)
    suggested_journals: list[dict[str, Any]] = field(default_factory=list)
    search_queries: list[dict[str, Any]] = field(default_factory=list)
    open_access_links: list[dict[str, Any]] = field(default_factory=list)
    publication_recommendation: dict[str, Any] = field(default_factory=dict)
    scopus_verification_note: str = ""
    generated_by_model: str = ""
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @staticmethod
    def json_to_dict(value: Any, fallback: Any):
        if value in (None, ""):
            return fallback
        if isinstance(value, (dict, list)):
            return value
        if not isinstance(value, str):
            return fallback
        try:
            parsed = json.loads(value)
            if isinstance(fallback, dict) and isinstance(parsed, dict):
                return parsed
            if isinstance(fallback, list) and isinstance(parsed, list):
                return parsed
            return fallback
        except (TypeError, ValueError, json.JSONDecodeError):
            return fallback

    @staticmethod
    def dict_to_json(value: Any) -> str:
        try:
            return json.dumps(value if value is not None else {}, ensure_ascii=False)
        except (TypeError, ValueError):
            return "{}"

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "recommendation_id": self.recommendation_id,
            "user_id": self.user_id,
            "research_type": self.research_type,
            "research_title": self.research_title,
            "research_inputs": self.research_inputs,
            "research_draft": self.research_draft,
            "suggested_journals": self.suggested_journals,
            "search_queries": self.search_queries,
            "open_access_links": self.open_access_links,
            "publication_recommendation": self.publication_recommendation,
            "scopus_verification_note": self.scopus_verification_note,
            "generated_by_model": self.generated_by_model,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    @classmethod
    def from_db_row(cls, row: Mapping[str, Any]) -> "ResearchOutput":
        return cls(
            id=int(row.get("id") or 0),
            recommendation_id=int(row.get("recommendation_id") or 0),
            user_id=(int(row["user_id"]) if row.get("user_id") is not None else None),
            research_type=str(row.get("research_type") or ""),
            research_title=str(row.get("research_title") or ""),
            research_inputs=cls.json_to_dict(row.get("research_inputs_json"), {}),
            research_draft=cls.json_to_dict(row.get("research_draft_json"), {}),
            suggested_journals=cls.json_to_dict(row.get("suggested_journals_json"), []),
            search_queries=cls.json_to_dict(row.get("search_queries_json"), []),
            open_access_links=cls.json_to_dict(row.get("open_access_links_json"), []),
            publication_recommendation=cls.json_to_dict(
                row.get("publication_recommendation_json"),
                {},
            ),
            scopus_verification_note=str(row.get("scopus_verification_note") or ""),
            generated_by_model=str(row.get("generated_by_model") or ""),
            created_at=(from_db(row["created_at"]) if row.get("created_at") else None),
            updated_at=(from_db(row["updated_at"]) if row.get("updated_at") else None),
        )

    @classmethod
    def from_db_row_optional(cls, row: Optional[Mapping[str, Any]]) -> Optional["ResearchOutput"]:
        return cls.from_db_row(row) if row is not None else None
