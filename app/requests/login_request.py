"""LoginRequest — validates the login form."""

from __future__ import annotations

from dataclasses import dataclass

from app.requests.base_request import BaseRequest, Rule
from app.utils.validators import is_non_empty, min_length, sanitize


@dataclass
class LoginRequest(BaseRequest):
    identifier: str = ""  # email or username
    password: str = ""

    def sanitize(self) -> None:
        self.identifier = sanitize(self.identifier)
        # Don't strip passwords beyond outer whitespace, but trim leading/trailing
        self.password = self.password.strip() if isinstance(self.password, str) else ""

    def rules(self) -> list[Rule]:
        return [
            ("identifier", is_non_empty, "Please enter your email or username."),
            ("password", is_non_empty, "Please enter your password."),
            ("password", lambda v: min_length(v, 6), "Password must be at least 6 characters."),
        ]
