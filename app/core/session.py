"""In-memory user session.

Backed by Flet's ``page.client_storage`` for persistence across launches,
but exposed as a simple object the rest of the app can depend on.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import flet as ft

from app.models.user import User
from ui.theme import hydrate_theme_after_login

_USER_ID_KEY = "stackwise.session.user_id"


@dataclass
class Session:
    page: ft.Page
    user: Optional[User] = None

    @property
    def is_authenticated(self) -> bool:
        return self.user is not None

    def login(self, user: User) -> None:
        self.user = user
        try:
            self.page.client_storage.set(_USER_ID_KEY, user.id)
        except Exception:
            pass
        try:
            hydrate_theme_after_login(self.page, user)
        except Exception:
            pass

    def logout(self) -> None:
        self.user = None
        try:
            self.page.client_storage.remove(_USER_ID_KEY)
        except Exception:
            pass

    def stored_user_id(self) -> Optional[int]:
        try:
            value = self.page.client_storage.get(_USER_ID_KEY)
            return int(value) if value is not None else None
        except Exception:
            return None
