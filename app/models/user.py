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
    password_hash: str
    created_at: datetime

    @staticmethod
    def from_row(row: Mapping[str, Any]) -> "User":
        return User(
            id=int(row["id"]),
            full_name=row["full_name"],
            username=row["username"],
            email=row["email"],
            password_hash=row["password_hash"],
            created_at=from_db(row["created_at"]),
        )

    @staticmethod
    def from_row_optional(row: Optional[Mapping[str, Any]]) -> Optional["User"]:
        return User.from_row(row) if row is not None else None
