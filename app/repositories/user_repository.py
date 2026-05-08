"""User repository — MySQL access for the users table."""

from __future__ import annotations

from typing import Optional

from app.models.user import User
from app.repositories.base_repository import BaseRepository


class UserRepository(BaseRepository):
    def find_by_email(self, email: str) -> Optional[User]:
        row = self.db.fetch_one(
            "SELECT * FROM users WHERE email = %s LIMIT 1",
            (email.lower().strip(),),
        )
        return User.from_row_optional(row)

    def find_by_username(self, username: str) -> Optional[User]:
        row = self.db.fetch_one(
            "SELECT * FROM users WHERE username = %s LIMIT 1",
            (username.strip(),),
        )
        return User.from_row_optional(row)

    def find_by_email_or_username(self, identifier: str) -> Optional[User]:
        ident = identifier.strip()
        row = self.db.fetch_one(
            "SELECT * FROM users WHERE email = %s OR username = %s LIMIT 1",
            (ident.lower(), ident),
        )
        return User.from_row_optional(row)

    def find_by_id(self, user_id: int) -> Optional[User]:
        row = self.db.fetch_one(
            "SELECT * FROM users WHERE id = %s LIMIT 1",
            (user_id,),
        )
        return User.from_row_optional(row)

    def create(
        self,
        full_name: str,
        username: str,
        email: str,
        password_hash: str,
    ) -> User:
        new_id = self.db.execute(
            "INSERT INTO users (full_name, username, email, password_hash) "
            "VALUES (%s, %s, %s, %s)",
            (full_name.strip(), username.strip(), email.lower().strip(), password_hash),
        )
        user = self.find_by_id(new_id)
        assert user is not None, "User insert returned no row"
        return user

    def update_password(self, user_id: int, password_hash: str) -> None:
        self.db.execute(
            "UPDATE users SET password_hash = %s WHERE id = %s",
            (password_hash, user_id),
        )

    def count(self) -> int:
        row = self.db.fetch_one("SELECT COUNT(*) AS c FROM users")
        return int(row["c"]) if row else 0
