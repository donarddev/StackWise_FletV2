"""Empty-state placeholder used across pages with no content yet."""

from __future__ import annotations

from typing import Any, Mapping, Optional

import flet as ft

from ui.components.glass_card import glass_card
from ui.themes.app_theme import Colors, Spacing, Typography
from ui.theme import subheading_style, text_style


def empty_state(
    *,
    icon: Optional[str] = None,
    title: str,
    description: str,
    action: Optional[ft.Control] = None,
    theme: Optional[Mapping[str, Any]] = None,
) -> ft.Control:
    if icon is None:
        icon = "lightbulb_outline"
    if theme is not None:
        accent = theme["accent"]
        body = ft.Column(
            spacing=Spacing.md,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Container(
                    width=72, height=72, border_radius=20,
                    bgcolor=ft.colors.with_opacity(0.10, accent),
                    alignment=ft.alignment.center,
                    content=ft.Icon(icon, size=32, color=theme["accent_soft"]),
                ),
                ft.Text(title, style=subheading_style(theme, size=18), text_align=ft.TextAlign.CENTER),
                ft.Text(description, style=text_style(theme, size=14), text_align=ft.TextAlign.CENTER),
                *( [ft.Container(height=Spacing.sm), action] if action else [] ),
            ],
        )
        return glass_card(
            ft.Container(content=body, padding=Spacing.xl, alignment=ft.alignment.center),
            padding=0,
            theme=theme,
        )
    body = ft.Column(
        spacing=Spacing.md,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        controls=[
            ft.Container(
                width=72, height=72, border_radius=20,
                bgcolor=ft.colors.with_opacity(0.10, Colors.primary),
                alignment=ft.alignment.center,
                content=ft.Icon(icon, size=32, color=Colors.primary_glow),
            ),
            ft.Text(title, style=Typography.subheading(size=18), text_align=ft.TextAlign.CENTER),
            ft.Text(description, style=Typography.body(), text_align=ft.TextAlign.CENTER),
            *( [ft.Container(height=Spacing.sm), action] if action else [] ),
        ],
    )
    return glass_card(
        ft.Container(content=body, padding=Spacing.xl, alignment=ft.alignment.center),
        padding=0,
    )
