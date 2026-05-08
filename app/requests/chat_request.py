"""ChatRequest — validates a single chatbot turn."""

from __future__ import annotations

from dataclasses import dataclass

from app.requests.base_request import BaseRequest, Rule
from app.utils.validators import is_non_empty, max_length


@dataclass
class ChatRequest(BaseRequest):
    message: str = ""

    def sanitize(self) -> None:
        if isinstance(self.message, str):
            self.message = self.message.strip()

    def rules(self) -> list[Rule]:
        return [
            ("message", is_non_empty, "Type a message first."),
            ("message", lambda v: max_length(v, 4000), "Message is too long (max 4000 chars)."),
        ]
