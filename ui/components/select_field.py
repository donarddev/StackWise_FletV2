"""Premium dropdown / select field."""

from __future__ import annotations

from typing import Any, Iterable, Mapping, Optional

import flet as ft

from ui.themes.app_theme import Colors, Radii


def select_field(
    label: str,
    options: Iterable[str],
    *,
    value: Optional[str] = None,
    hint: Optional[str] = None,
    on_change=None,
    theme: Optional[Mapping[str, Any]] = None,
) -> ft.Dropdown:
    if theme is not None:
        return ft.Dropdown(
            label=label,
            hint_text=hint,
            value=value,
            on_change=on_change,
            options=[ft.dropdown.Option(o) for o in options],
            bgcolor=theme["surface"],
            border_color=theme["border_strong"],
            focused_border_color=theme["accent"],
            focused_bgcolor=theme["surface_3"],
            color=theme["text"],
            text_style=ft.TextStyle(color=theme["text"], size=14),
            label_style=ft.TextStyle(color=theme["text_secondary"], size=13),
            hint_style=ft.TextStyle(color=theme["text_muted"], size=13),
            border_radius=Radii.md,
            content_padding=ft.padding.symmetric(horizontal=14, vertical=14),
        )
    return ft.Dropdown(
        label=label,
        hint_text=hint,
        value=value,
        on_change=on_change,
        options=[ft.dropdown.Option(o) for o in options],
        bgcolor=Colors.surface,
        border_color=Colors.border,
        focused_border_color=Colors.primary,
        focused_bgcolor=Colors.surface_3,
        color=Colors.text_primary,
        text_style=ft.TextStyle(color=Colors.text_primary, size=14),
        label_style=ft.TextStyle(color=Colors.text_secondary, size=13),
        hint_style=ft.TextStyle(color=Colors.text_muted, size=13),
        border_radius=Radii.md,
        content_padding=ft.padding.symmetric(horizontal=14, vertical=14),
    )
