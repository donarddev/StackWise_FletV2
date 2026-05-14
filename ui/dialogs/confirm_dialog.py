"""Confirmation dialog helpers."""

from __future__ import annotations

from typing import Any, Callable, Mapping

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


def show_sign_out_dialog(
    page: ft.Page,
    *,
    on_confirm: Callable[[], None],
    theme: Mapping[str, Any],
) -> None:
    show_confirmation_dialog(
        page,
        theme=theme,
        title="Sign out of StackWise AI?",
        message=(
            "You are about to end your current session. You can sign in again "
            "anytime using your account."
        ),
        icon=ft.icons.LOGOUT_ROUNDED,
        confirm_label="Sign out",
        confirm_icon=ft.icons.LOGOUT_ROUNDED,
        confirm_kind="danger",
        on_confirm=on_confirm,
    )


def show_confirmation_dialog(
    page: ft.Page,
    *,
    theme: Mapping[str, Any],
    title: str,
    message: str,
    icon: str,
    confirm_label: str,
    confirm_icon: str,
    confirm_kind: str = "danger",
    on_confirm: Callable[[], None],
) -> None:
    """Open a themed modal and close it via page.dialog to avoid stale overlays."""
    accent = theme["danger"] if confirm_kind == "danger" else theme["warning"]

    def close_dialog(_e: ft.ControlEvent | None = None) -> None:
        dialog.open = False
        page.update()

    def confirm_action(_e: ft.ControlEvent) -> None:
        close_dialog()
        on_confirm()

    dialog = ft.AlertDialog(
        modal=True,
        alignment=ft.alignment.center,
        bgcolor=theme["card_bg"],
        surface_tint_color=theme["card_bg"],
        shadow_color=theme["card_shadow_color"],
        inset_padding=ft.padding.symmetric(horizontal=24, vertical=24),
        title_padding=ft.padding.only(left=24, right=24, top=24, bottom=8),
        content_padding=ft.padding.only(left=24, right=24, top=0, bottom=8),
        actions_padding=ft.padding.only(left=24, right=24, top=8, bottom=24),
        shape=ft.RoundedRectangleBorder(radius=18),
        title=ft.Row(
            spacing=12,
            controls=[
                ft.Container(
                    width=42,
                    height=42,
                    border_radius=14,
                    alignment=ft.alignment.center,
                    bgcolor=ft.colors.with_opacity(0.14, accent),
                    border=ft.border.all(1, ft.colors.with_opacity(0.38, accent)),
                    content=ft.Icon(icon, size=20, color=accent),
                ),
                ft.Text(title, size=20, weight=ft.FontWeight.W_700, color=theme["text"]),
            ],
        ),
        content=ft.Container(
            width=420,
            content=ft.Text(message, size=14, color=theme["text_secondary"], height=1.45),
        ),
        actions_alignment=ft.MainAxisAlignment.END,
        actions=[
            _dialog_button(
                "Cancel",
                icon=ft.icons.CLOSE_ROUNDED,
                theme=theme,
                on_click=close_dialog,
            ),
            _dialog_button(
                confirm_label,
                icon=confirm_icon,
                theme=theme,
                on_click=confirm_action,
                accent=accent,
                filled=True,
            ),
        ],
    )
    page.dialog = dialog
    dialog.open = True
    page.update()


def _dialog_button(
    text: str,
    *,
    icon: str,
    theme: Mapping[str, Any],
    on_click: Callable[[ft.ControlEvent], None],
    accent: str | None = None,
    filled: bool = False,
) -> ft.Container:
    fg = theme["on_gradient"] if filled else theme["text"]
    bg = accent if filled and accent else theme["secondary_surface"]
    border_color = ft.colors.with_opacity(0.45, accent) if filled and accent else theme["border_strong"]

    def on_hover(e: ft.ControlEvent) -> None:
        e.control.scale = ft.Scale(1.02 if e.data == "true" else 1)
        if e.control.page:
            e.control.update()

    return ft.Container(
        content=ft.Row(
            tight=True,
            spacing=8,
            alignment=ft.MainAxisAlignment.CENTER,
            controls=[
                ft.Icon(icon, size=17, color=fg),
                ft.Text(text, size=13, weight=ft.FontWeight.W_700, color=fg),
            ],
        ),
        padding=ft.padding.symmetric(horizontal=16, vertical=10),
        border_radius=12,
        bgcolor=bg,
        border=ft.border.all(1, border_color),
        ink=True,
        scale=ft.Scale(1),
        animate_scale=ft.Animation(140, ft.AnimationCurve.EASE_OUT),
        on_hover=on_hover,
        on_click=on_click,
    )
