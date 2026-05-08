"""Confirmation dialog helper."""

from __future__ import annotations

from typing import Callable

import flet as ft

from ui.themes.app_theme import Colors, Radii


def confirm_dialog(
    *,
    title: str,
    message: str,
    confirm_label: str = "Confirm",
    cancel_label: str = "Cancel",
    on_confirm: Callable[[ft.ControlEvent], None],
    on_cancel: Callable[[ft.ControlEvent], None],
) -> ft.AlertDialog:
    return ft.AlertDialog(
        modal=True,
        bgcolor=Colors.surface,
        shape=ft.RoundedRectangleBorder(radius=Radii.lg),
        title=ft.Text(title, color=Colors.text_primary),
        content=ft.Text(message, color=Colors.text_secondary),
        actions=[
            ft.TextButton(cancel_label, on_click=on_cancel),
            ft.FilledButton(confirm_label, on_click=on_confirm),
        ],
    )
