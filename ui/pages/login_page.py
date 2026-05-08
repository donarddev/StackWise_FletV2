"""Login page."""

from __future__ import annotations

from typing import Callable

import flet as ft

from ui.components.auth_brand_header import auth_brand_header
from ui.components.auth_text_field import auth_text_field
from ui.components.primary_button import primary_button, text_link
from ui.components.validation_message import validation_message
from ui.layouts.auth_layout import auth_layout
from ui.themes.app_theme import Colors, Spacing, Typography


def build_login_page(
    *,
    on_login: Callable[[str, str], None],
    on_go_register: Callable[[ft.ControlEvent], None],
    error_container_ref: ft.Ref[ft.Container],
    error_text_ref: ft.Ref[ft.Text],
    submitting_ref: ft.Ref[ft.ProgressRing],
    submit_ref: ft.Ref[ft.Container],
    fields: dict[str, ft.TextField],
) -> ft.Control:
    form = build_login_form(
        on_login=on_login,
        on_go_register=on_go_register,
        error_container_ref=error_container_ref,
        error_text_ref=error_text_ref,
        submitting_ref=submitting_ref,
        submit_ref=submit_ref,
        fields=fields,
    )
    return auth_layout(form)


def build_login_form(
    *,
    on_login: Callable[[str, str], None],
    on_go_register: Callable[[ft.ControlEvent], None],
    error_container_ref: ft.Ref[ft.Container],
    error_text_ref: ft.Ref[ft.Text],
    submitting_ref: ft.Ref[ft.ProgressRing],
    submit_ref: ft.Ref[ft.Container],
    fields: dict[str, ft.TextField],
) -> ft.Control:
    fields["identifier"] = auth_text_field(
        "Email or username", icon=ft.icons.PERSON_OUTLINE, autofocus=True,
    )
    fields["password"] = auth_text_field(
        "Password", icon=ft.icons.LOCK_OUTLINE, password=True,
        on_submit=lambda _e: on_login(
            fields["identifier"].value or "", fields["password"].value or ""
        ),
    )

    error = validation_message(container_ref=error_container_ref, text_ref=error_text_ref)

    submitting = ft.ProgressRing(
        width=18, height=18, stroke_width=2, color=Colors.primary_glow,
        visible=False, ref=submitting_ref,
    )

    submit = primary_button(
        "Sign in",
        on_click=lambda _e: on_login(
            fields["identifier"].value or "", fields["password"].value or ""
        ),
        icon=ft.icons.LOGIN_ROUNDED,
        expand=True,
        ref=submit_ref,
    )

    form = ft.Column(
        spacing=10,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        controls=[
            auth_brand_header(),
            ft.Container(height=Spacing.md),
            ft.Text("Welcome back", style=Typography.heading(size=28, weight=ft.FontWeight.W_700), text_align=ft.TextAlign.CENTER),
            ft.Text(
                "Continue planning smarter software projects with StackWise AI.",
                style=Typography.body(size=13.5),
                text_align=ft.TextAlign.CENTER,
            ),
            ft.Container(height=Spacing.md),
            fields["identifier"],
            fields["password"],
            error,
            ft.Container(height=Spacing.xs),
            ft.Row(
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[submit, submitting],
                spacing=Spacing.md,
            ),
            ft.Container(height=Spacing.sm),
            ft.Row(
                spacing=4,
                controls=[
                    ft.Text("New here?", style=Typography.body(size=13)),
                    text_link("Create an account", on_click=on_go_register),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
            ),
        ],
    )
    return form
