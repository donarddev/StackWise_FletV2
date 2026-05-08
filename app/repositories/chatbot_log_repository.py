"""Chatbot log repository — chat history persistence."""

from __future__ import annotations

from typing import Optional

from app.models.chatbot_log import ChatbotLog, Role
from app.repositories.base_repository import BaseRepository


class ChatbotLogRepository(BaseRepository):
    def append(
        self,
        user_id: int,
        role: Role,
        content: str,
        model: Optional[str] = None,
    ) -> ChatbotLog:
        new_id = self.db.execute(
            "INSERT INTO chatbot_logs (user_id, role, content, model) VALUES (%s, %s, %s, %s)",
            (user_id, role, content, model),
        )
        row = self.db.fetch_one("SELECT * FROM chatbot_logs WHERE id = %s", (new_id,))
        assert row is not None
        return ChatbotLog.from_row(row)

    def list_for_user(self, user_id: int, limit: int = 200) -> list[ChatbotLog]:
        rows = self.db.fetch_all(
            "SELECT * FROM chatbot_logs WHERE user_id = %s "
            "ORDER BY created_at ASC, id ASC LIMIT %s",
            (user_id, int(limit)),
        )
        return [ChatbotLog.from_row(r) for r in rows]

    def clear_for_user(self, user_id: int) -> None:
        self.db.execute("DELETE FROM chatbot_logs WHERE user_id = %s", (user_id,))
