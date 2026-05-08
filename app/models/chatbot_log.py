"""ChatbotLog entity — one row per message exchanged with the assistant."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Literal, Mapping, Optional

from app.helpers.date_helper import from_db


Role = Literal["user", "assistant", "system"]


@dataclass
class ChatbotLog:
    id: int
    user_id: int
    role: Role
    content: str
    model: Optional[str]
    created_at: datetime

    @staticmethod
    def from_row(row: Mapping[str, Any]) -> "ChatbotLog":
        return ChatbotLog(
            id=int(row["id"]),
            user_id=int(row["user_id"]),
            role=row["role"],
            content=row["content"],
            model=row["model"],
            created_at=from_db(row["created_at"]),
        )
