from __future__ import annotations

from typing import Callable, Optional

import flet as ft

from ui.themes.app_theme import Colors, Radii, Spacing


def google_button(
    text: str,
    on_click: Callable[[ft.ControlEvent], None],
    *,
    loading: bool = False,
    expand: bool | int = False,
    ref: Optional[ft.Ref[ft.Container]] = None,
) -> ft.Container:
    label = ft.Row(
        controls=[
            ft.Container(
                content=ft.Text("G", weight=ft.FontWeight.W_800, size=16, color=Colors.text_primary),
                width=28,
                height=28,
                alignment=ft.alignment.center,
                border_radius=28,
                bgcolor=Colors.surface_2,
            ),
            ft.Text(text, size=14, weight=ft.FontWeight.W_600, color=Colors.text_primary),
        ],
        spacing=Spacing.sm,
        alignment=ft.MainAxisAlignment.CENTER,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
        tight=True,
    )

    return ft.Container(
        ref=ref,
        content=label,
        border=ft.border.all(1, Colors.border_strong),
        bgcolor=Colors.surface_2,
        border_radius=Radii.md,
        padding=ft.padding.symmetric(horizontal=22, vertical=12),
        height=46,
        ink=True,
        on_click=None if loading else on_click,
        opacity=0.55 if loading else 1.0,
        expand=expand,
        alignment=ft.alignment.center,
    )
