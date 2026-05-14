"""User entity. Pure data, no behavior beyond row mapping."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Mapping, Optional

from app.helpers.date_helper import from_db


@dataclass
class User:
    id: int
    full_name: str
    username: str
    email: str
    password_hash: Optional[str]
    created_at: datetime
    google_id: Optional[str] = None
    provider: str = "local"
    avatar_url: Optional[str] = None
    theme_mode: Optional[str] = None

    @staticmethod
    def from_row(row: Mapping[str, Any]) -> "User":
        tm = row.get("theme_mode")
        if tm is not None and tm not in ("dark", "light"):
            tm = None
        return User(
            id=int(row["id"]),
            full_name=row.get("full_name", ""),
            username=row.get("username", ""),
            email=row.get("email", ""),
            password_hash=row.get("password_hash"),
            created_at=from_db(row["created_at"]),
            google_id=row.get("google_id"),
            provider=row.get("provider", "local"),
            avatar_url=row.get("avatar_url"),
            theme_mode=tm,
        )

    @staticmethod
    def from_row_optional(row: Optional[Mapping[str, Any]]) -> Optional["User"]:
        return User.from_row(row) if row is not None else None
