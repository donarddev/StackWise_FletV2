"""ValidationMessage — elegant inline form feedback."""

from __future__ import annotations

import flet as ft

from ui.themes.app_theme import Colors, Radii, Spacing, Typography


def validation_message(
    *,
    container_ref: ft.Ref[ft.Container],
    text_ref: ft.Ref[ft.Text],
) -> ft.Control:
    """Returns a message container controllable via refs.

    Controllers should toggle container visibility and set the text value.
    """
    return ft.Container(
        ref=container_ref,
        visible=False,
        padding=ft.padding.symmetric(horizontal=12, vertical=10),
        bgcolor=ft.colors.with_opacity(0.10, Colors.danger),
        border=ft.border.all(1, ft.colors.with_opacity(0.35, Colors.danger)),
        border_radius=Radii.md,
        content=ft.Row(
            spacing=Spacing.sm,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Icon(ft.icons.INFO_OUTLINE, size=16, color=ft.colors.with_opacity(0.9, Colors.danger)),
                ft.Text(
                    "",
                    ref=text_ref,
                    size=12.5,
                    color=ft.colors.with_opacity(0.92, Colors.text_primary),
                ),
            ],
        ),
    )

