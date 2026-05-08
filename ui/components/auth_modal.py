"""Auth modal overlay wrappers for login/register forms."""

from __future__ import annotations

import flet as ft

from ui.components.auth_card import auth_card
from ui.themes.app_theme import Colors, Radii, Spacing


def auth_modal(*, form: ft.Control, on_close) -> ft.AlertDialog:
    return ft.AlertDialog(
        modal=True,
        bgcolor=ft.colors.TRANSPARENT,
        shape=ft.RoundedRectangleBorder(radius=Radii.xl),
        inset_padding=ft.padding.symmetric(horizontal=28, vertical=20),
        content=ft.Container(
            width=458,
            content=auth_card(
                ft.Column(
                    spacing=Spacing.md,
                    controls=[
                        ft.Row(
                            alignment=ft.MainAxisAlignment.END,
                            controls=[
                                ft.IconButton(
                                    icon=ft.icons.CLOSE_ROUNDED,
                                    icon_size=18,
                                    icon_color=Colors.text_secondary,
                                    tooltip="Close",
                                    on_click=on_close,
                                ),
                            ],
                        ),
                        form,
                    ],
                ),
                width=452,
            ),
        ),
    )
