"""User repository — MySQL access for the users table."""

from __future__ import annotations

import re
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

    def find_by_google_id(self, google_id: str) -> Optional[User]:
        row = self.db.fetch_one(
            "SELECT * FROM users WHERE google_id = %s LIMIT 1",
            (google_id.strip(),),
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

    def create_google_user(
        self,
        full_name: str,
        email: str,
        google_id: str,
        avatar_url: str | None = None,
    ) -> User:
        # Derive a username compatible with normal registration rules.
        base = re.sub(r"[^A-Za-z0-9_.-]", "_", email.split("@")[0]).strip("._-")
        if len(base) < 3:
            base = "google_user"
        base = base[:32]
        username = base
        existing = self.find_by_username(username)
        if existing is not None:
            suffix = int(self.db.fetch_one("SELECT UNIX_TIMESTAMP() AS t")["t"])
            username = f"{base[: max(3, 31 - len(str(suffix)))]}_{suffix}"[:32]

        new_id = self.db.execute(
            "INSERT INTO users (full_name, username, email, password_hash, google_id, provider, avatar_url) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s)",
            (
                (full_name or email.split("@")[0]).strip(),
                username.strip(),
                email.lower().strip(),
                None,
                google_id,
                "google",
                avatar_url,
            ),
        )
        user = self.find_by_id(new_id)
        assert user is not None, "User insert returned no row"
        return user

    def link_google_account(self, user_id: int, google_id: str, avatar_url: str | None = None) -> None:
        self.db.execute(
            "UPDATE users SET google_id = %s, provider = %s, avatar_url = %s WHERE id = %s",
            (google_id, "google", avatar_url, user_id),
        )

    def update_password(self, user_id: int, password_hash: str) -> None:
        self.db.execute(
            "UPDATE users SET password_hash = %s WHERE id = %s",
            (password_hash, user_id),
        )

    def update_theme_preference(self, user_id: int, mode: str) -> None:
        if mode not in ("dark", "light"):
            return
        self.db.execute(
            "UPDATE users SET theme_mode = %s WHERE id = %s",
            (mode, user_id),
        )

    def count(self) -> int:
        row = self.db.fetch_one("SELECT COUNT(*) AS c FROM users")
        return int(row["c"]) if row else 0
