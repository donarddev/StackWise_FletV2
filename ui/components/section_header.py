"""SectionHeader — title + subtitle + optional trailing action."""

from __future__ import annotations

from typing import Optional

import flet as ft

from ui.themes.app_theme import Spacing, Typography


def section_header(
    title: str,
    *,
    subtitle: Optional[str] = None,
    trailing: Optional[ft.Control] = None,
) -> ft.Row:
    column = ft.Column(
        controls=[
            ft.Text(title, style=Typography.heading(size=22)),
            *( [ft.Text(subtitle, style=Typography.body())] if subtitle else [] ),
        ],
        spacing=4,
        tight=True,
    )

    return ft.Row(
        controls=[
            column,
            ft.Container(expand=1),
            *( [trailing] if trailing else [] ),
        ],
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
    )
