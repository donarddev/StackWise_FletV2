"""Premium text input field, matching the dark theme."""

from __future__ import annotations

from typing import Optional

import flet as ft

from ui.themes.app_theme import Colors, Radii


def input_field(
    label: str,
    *,
    value: str = "",
    hint: Optional[str] = None,
    password: bool = False,
    icon: Optional[str] = None,
    multiline: bool = False,
    min_lines: int = 1,
    max_lines: int = 1,
    on_change=None,
    on_submit=None,
    autofocus: bool = False,
    text_size: int = 14,
) -> ft.TextField:
    return ft.TextField(
        label=label,
        value=value,
        hint_text=hint,
        password=password,
        can_reveal_password=password,
        prefix_icon=icon,
        multiline=multiline,
        min_lines=min_lines,
        max_lines=max_lines if multiline else 1,
        autofocus=autofocus,
        text_size=text_size,
        on_change=on_change,
        on_submit=on_submit,
        bgcolor=Colors.surface,
        border_color=Colors.border,
        focused_border_color=Colors.primary,
        focused_bgcolor=Colors.surface_3,
        cursor_color=Colors.primary_soft,
        color=Colors.text_primary,
        label_style=ft.TextStyle(color=Colors.text_secondary, size=13),
        hint_style=ft.TextStyle(color=Colors.text_muted, size=13),
        text_style=ft.TextStyle(color=Colors.text_primary, size=text_size),
        border_radius=Radii.md,
        content_padding=ft.padding.symmetric(horizontal=14, vertical=14),
    )
