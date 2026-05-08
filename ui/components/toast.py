"""Toast / snackbar helpers."""

from __future__ import annotations

import flet as ft

from ui.themes.app_theme import Colors


def show_toast(page: ft.Page, message: str, *, kind: str = "info") -> None:
    color = {
        "info": Colors.primary,
        "success": Colors.success,
        "error": Colors.danger,
        "warning": Colors.warning,
    }.get(kind, Colors.primary)

    page.snack_bar = ft.SnackBar(
        content=ft.Text(message, color=Colors.text_primary),
        bgcolor=Colors.surface_3,
        action="OK",
        action_color=color,
        behavior=ft.SnackBarBehavior.FLOATING,
    )
    page.snack_bar.open = True
    page.update()
