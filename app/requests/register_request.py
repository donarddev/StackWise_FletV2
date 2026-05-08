"""RegisterRequest — validates account creation."""

from __future__ import annotations

from dataclasses import dataclass

from app.requests.base_request import BaseRequest, Rule
from app.utils.validators import (
    is_email,
    is_non_empty,
    is_username,
    min_length,
    sanitize,
)


@dataclass
class RegisterRequest(BaseRequest):
    full_name: str = ""
    username: str = ""
    email: str = ""
    password: str = ""
    confirm_password: str = ""

    def sanitize(self) -> None:
        self.full_name = sanitize(self.full_name)
        self.username = sanitize(self.username)
        self.email = sanitize(self.email).lower()
        self.password = self.password.strip() if isinstance(self.password, str) else ""
        self.confirm_password = (
            self.confirm_password.strip()
            if isinstance(self.confirm_password, str)
            else ""
        )

    def rules(self) -> list[Rule]:
        return [
            ("full_name", is_non_empty, "Please enter your full name."),
            ("full_name", lambda v: min_length(v, 2), "Full name must be at least 2 characters."),
            ("username", is_non_empty, "Please enter a username."),
            ("username", is_username, "Username must be 3–32 chars: letters, digits, _ . -"),
            ("email", is_non_empty, "Please enter your email."),
            ("email", is_email, "Email looks invalid."),
            ("password", is_non_empty, "Please enter your password."),
            ("password", lambda v: min_length(v, 6), "Password must be at least 6 characters."),
            ("confirm_password", lambda v: v == self.password, "Passwords do not match."),
        ]
