"""Reusable chat message chrome (Flet) — user identity header and avatar.

Used by ``ui.widgets.chat_bubble`` to mirror assistant header layout without
duplicating styling logic.
"""

from __future__ import annotations

from typing import Any, Mapping

import flet as ft

from ui.components.dashboard.glass_tokens import dashboard_glass_tokens
from ui.themes.app_theme import Colors

_AVATAR_PX = 32


def default_user_header_title(author_name: str, *, title_override: str | None = None) -> str:
    """Short label above the user bubble (first name, or ``You`` if unknown)."""
    if title_override is not None and title_override.strip():
        return title_override.strip()
    parts = (author_name or "").strip().split()
    if not parts:
        return "You"
    return parts[0]


def user_initial_letter(author_name: str) -> str:
    """Single letter for circular fallback avatar."""
    s = (author_name or "").strip()
    if not s:
        return "U"
    return s[0].upper()


def build_user_avatar(
    *,
    author_name: str,
    avatar_url: str | None,
    theme: Mapping[str, Any] | None,
) -> ft.Control:
    """Circular user avatar: remote image when URL is set, else initial letter."""
    url = (avatar_url or "").strip() or None
    if theme is not None:
        g = dashboard_glass_tokens(theme)
        user_avatar_bg = theme["surface_3"]
        if str(theme.get("page_bg", "")).lower() == "#020617":
            user_border_col = g["card_border"]
            glow = ft.colors.with_opacity(0.12, g["teal"])
        else:
            user_border_col = ft.colors.with_opacity(0.45, theme["accent_2"])
            glow = ft.colors.with_opacity(0.12, theme["accent_2"])
        avatar_fg = theme["text"]
    else:
        user_avatar_bg = Colors.surface_3
        user_border_col = ft.colors.with_opacity(0.4, Colors.accent_cyan)
        avatar_fg = Colors.text_primary
        glow = ft.colors.with_opacity(0.14, Colors.accent_cyan)

    ring = ft.border.all(1, user_border_col)
    shadow = ft.BoxShadow(
        spread_radius=0,
        blur_radius=6,
        color=glow,
        offset=ft.Offset(0, 1),
    )
    r = _AVATAR_PX // 2

    if url:
        return ft.Container(
            width=_AVATAR_PX,
            height=_AVATAR_PX,
            border_radius=r,
            clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
            border=ring,
            shadow=shadow,
            bgcolor=user_avatar_bg if theme is not None else Colors.surface_2,
            content=ft.Image(
                src=url,
                width=_AVATAR_PX,
                height=_AVATAR_PX,
                fit=ft.ImageFit.COVER,
                border_radius=r,
            ),
        )

    letter = user_initial_letter(author_name)
    return ft.Container(
        width=_AVATAR_PX,
        height=_AVATAR_PX,
        border_radius=r,
        alignment=ft.alignment.center,
        bgcolor=user_avatar_bg,
        border=ring,
        shadow=shadow,
        content=ft.Text(
            letter,
            size=13,
            weight=ft.FontWeight.W_700,
            color=avatar_fg,
        ),
    )


def build_user_identity_header_row(
    *,
    title: str,
    author_name: str,
    avatar_url: str | None,
    theme: Mapping[str, Any] | None,
    name_style: ft.TextStyle,
) -> ft.Row:
    """Top-right identity strip: display name then avatar (aligned end)."""
    avatar = build_user_avatar(author_name=author_name, avatar_url=avatar_url, theme=theme)
    return ft.Row(
        tight=True,
        spacing=6,
        alignment=ft.MainAxisAlignment.END,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
        controls=[
            ft.Text(title, style=name_style),
            avatar,
        ],
    )
