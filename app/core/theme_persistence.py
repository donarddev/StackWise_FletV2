"""Persist workspace theme preference (client + authenticated user row)."""

from __future__ import annotations

import flet as ft

from ui.theme import THEME_MODE_DARK, THEME_MODE_LIGHT, get_theme_mode


def persist_user_theme_mode(page: ft.Page) -> None:
    """Save current theme_mode for the logged-in user (no-op if unauthenticated)."""
    c = getattr(page, "_stackwise_container", None)
    if c is None:
        return
    user = c.session.user
    if user is None:
        return
    mode = get_theme_mode(page)
    if mode not in (THEME_MODE_DARK, THEME_MODE_LIGHT):
        return
    try:
        c.user_repository.update_theme_preference(user.id, mode)
        user.theme_mode = mode
    except Exception:
        pass
