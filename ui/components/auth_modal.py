"""Auth modal overlay wrappers for login/register forms."""

from __future__ import annotations

import flet as ft

from ui.components.auth_card import auth_card
from ui.themes.app_theme import Colors, Radii, Spacing


def auth_modal(*, form: ft.Control, on_close, max_height: int | None = None) -> ft.AlertDialog:
    modal_height = max_height or 620
    scroll_region_height = max(320, modal_height - 92)
    return ft.AlertDialog(
        modal=True,
        bgcolor=ft.colors.TRANSPARENT,
        shape=ft.RoundedRectangleBorder(radius=Radii.xl),
        inset_padding=ft.padding.symmetric(horizontal=28, vertical=20),
        content=ft.Container(
            width=458,
            height=modal_height,
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
                        ft.Container(
                            height=scroll_region_height,
                            content=ft.ListView(
                                expand=True,
                                spacing=0,
                                auto_scroll=False,
                                padding=ft.padding.only(right=6, bottom=34),
                                controls=[form],
                            ),
                        ),
                    ],
                ),
                width=452,
            ),
        ),
    )
