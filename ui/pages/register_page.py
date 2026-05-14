"""Register page."""

from __future__ import annotations

from typing import Callable

import flet as ft

from ui.components.auth_brand_header import auth_brand_header
from ui.components.auth_text_field import auth_text_field
from ui.components.primary_button import primary_button, text_link
from ui.components.google_button import google_button
from ui.components.validation_message import validation_message
from ui.layouts.auth_layout import auth_layout
from ui.themes.app_theme import Colors, Spacing, Typography


def build_register_page(
    *,
    on_register: Callable[[dict[str, str]], None],
    on_google: Callable[[ft.ControlEvent], None],
    on_go_login: Callable[[ft.ControlEvent], None],
    error_container_ref: ft.Ref[ft.Container],
    error_text_ref: ft.Ref[ft.Text],
    submitting_ref: ft.Ref[ft.ProgressRing],
    submit_ref: ft.Ref[ft.Container],
    fields: dict[str, ft.TextField],
) -> ft.Control:
    form = build_register_form(
        on_register=on_register,
        on_google=on_google,
        on_go_login=on_go_login,
        error_container_ref=error_container_ref,
        error_text_ref=error_text_ref,
        submitting_ref=submitting_ref,
        submit_ref=submit_ref,
        fields=fields,
    )
    return auth_layout(form)


def build_register_form(
    *,
    on_register: Callable[[dict[str, str]], None],
    on_google: Callable[[ft.ControlEvent], None],
    on_go_login: Callable[[ft.ControlEvent], None],
    error_container_ref: ft.Ref[ft.Container],
    error_text_ref: ft.Ref[ft.Text],
    submitting_ref: ft.Ref[ft.ProgressRing],
    submit_ref: ft.Ref[ft.Container],
    fields: dict[str, ft.TextField],
) -> ft.Control:
    fields["full_name"] = auth_text_field("Full name", icon=ft.icons.BADGE_OUTLINED, autofocus=True)
    fields["username"] = auth_text_field("Username", icon=ft.icons.ALTERNATE_EMAIL)
    fields["email"] = auth_text_field("Email", icon=ft.icons.MAIL_OUTLINE)
    fields["password"] = auth_text_field("Password", icon=ft.icons.LOCK_OUTLINE, password=True)
    fields["confirm_password"] = auth_text_field(
        "Confirm password", icon=ft.icons.LOCK_OUTLINE, password=True,
        on_submit=lambda _e: on_register({k: (v.value or "") for k, v in fields.items()}),
    )

    error = validation_message(container_ref=error_container_ref, text_ref=error_text_ref)
    submitting = ft.ProgressRing(
        width=18, height=18, stroke_width=2, color=Colors.primary_glow,
        visible=False, ref=submitting_ref,
    )
    submit = primary_button(
        "Create account",
        on_click=lambda _e: on_register({k: (v.value or "") for k, v in fields.items()}),
        icon=ft.icons.ROCKET_LAUNCH_OUTLINED,
        expand=True,
        ref=submit_ref,
    )

    form = ft.Column(
        spacing=10,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        controls=[
            auth_brand_header(),
            ft.Container(height=Spacing.md),
            ft.Text("Create your account", style=Typography.heading(size=28, weight=ft.FontWeight.W_700), text_align=ft.TextAlign.CENTER),
            ft.Text(
                "Start generating explainable technology recommendations in minutes.",
                style=Typography.body(size=13.5),
                text_align=ft.TextAlign.CENTER,
            ),
            ft.Container(height=Spacing.md),
            fields["full_name"],
            fields["username"],
            fields["email"],
            fields["password"],
            fields["confirm_password"],
            error,
            ft.Container(height=Spacing.xs),
            ft.Container(
                padding=ft.padding.symmetric(vertical=6),
                content=ft.Row(
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[submit, submitting],
                    spacing=Spacing.md,
                ),
            ),
            ft.Container(height=Spacing.xs),
            ft.Row(
                spacing=8,
                alignment=ft.MainAxisAlignment.CENTER,
                controls=[
                    ft.Container(expand=True, content=ft.Divider(thickness=1, color=Colors.border)),
                    ft.Container(content=ft.Text("or", size=13, color=Colors.text_secondary)),
                    ft.Container(expand=True, content=ft.Divider(thickness=1, color=Colors.border)),
                ],
            ),
            ft.Container(height=Spacing.xs),
            google_button("Continue with Google", on_click=on_google, expand=True),
            ft.Container(height=Spacing.sm),
            ft.Container(height=Spacing.xs),
            ft.Row(
                spacing=4,
                controls=[
                    ft.Text("Already have an account?", style=Typography.body(size=13)),
                    text_link("Sign in", on_click=on_go_login),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
            ),
        ],
    )
    return form
