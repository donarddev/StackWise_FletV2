"""ChatBubble — message bubble for the chatbot UI."""

from __future__ import annotations

import flet as ft

from app.utils.constants import BRAND_INITIALS
from ui.themes.app_theme import Colors, Radii, Spacing, Typography


def chat_bubble(*, role: str, content: str, author_name: str = "") -> ft.Control:
    is_user = role == "user"
    bg = ft.colors.with_opacity(0.95, Colors.surface_2) if is_user else None
    grad = (
        None
        if is_user
        else ft.LinearGradient(
            begin=ft.alignment.top_left, end=ft.alignment.bottom_right,
            colors=["#1a1c40", "#0f172a"],
        )
    )
    border_color = Colors.border if is_user else ft.colors.with_opacity(0.4, Colors.primary)

    avatar = ft.Container(
        width=32, height=32, border_radius=10,
        alignment=ft.alignment.center,
        bgcolor=Colors.surface_3 if is_user else None,
        gradient=None if is_user else ft.LinearGradient(
            begin=ft.alignment.top_left, end=ft.alignment.bottom_right,
            colors=[Colors.primary, Colors.accent_cyan],
        ),
        content=ft.Text(
            (author_name[:1] or "U").upper() if is_user else BRAND_INITIALS,
            size=12, weight=ft.FontWeight.W_700, color=Colors.text_primary,
            text_align=ft.TextAlign.CENTER,
        ),
    )

    text = ft.Markdown(
        value=content,
        selectable=True,
        extension_set=ft.MarkdownExtensionSet.GITHUB_FLAVORED,
        code_theme="atom-one-dark",
    )

    bubble = ft.Container(
        content=text,
        bgcolor=bg,
        gradient=grad,
        padding=ft.padding.symmetric(horizontal=Spacing.lg, vertical=Spacing.md),
        border_radius=Radii.lg,
        border=ft.border.all(1, border_color),
        expand=True,
    )

    name_label = ft.Text(
        author_name if is_user else "StackWise AI",
        size=11, weight=ft.FontWeight.W_700, color=Colors.text_muted,
    )

    column = ft.Column(
        controls=[name_label, bubble],
        spacing=4, expand=True,
    )

    return ft.Row(
        controls=[avatar, column] if not is_user else [column, avatar],
        spacing=Spacing.md,
        vertical_alignment=ft.CrossAxisAlignment.START,
        alignment=ft.MainAxisAlignment.START if not is_user else ft.MainAxisAlignment.END,
    )


def typing_bubble() -> ft.Control:
    return ft.Row(
        controls=[
            ft.Container(
                width=32, height=32, border_radius=10,
                gradient=ft.LinearGradient(
                    begin=ft.alignment.top_left, end=ft.alignment.bottom_right,
                    colors=[Colors.primary, Colors.accent_cyan],
                ),
                alignment=ft.alignment.center,
                content=ft.Text(BRAND_INITIALS, size=12, weight=ft.FontWeight.W_700, color=Colors.text_primary),
            ),
            ft.Container(
                content=ft.Row(
                    controls=[
                        ft.ProgressRing(width=14, height=14, stroke_width=2, color=Colors.primary_glow),
                        ft.Text("Thinking…", style=Typography.body(size=13)),
                    ],
                    spacing=10,
                ),
                bgcolor=Colors.surface_2,
                border=ft.border.all(1, Colors.border),
                border_radius=Radii.lg,
                padding=ft.padding.symmetric(horizontal=Spacing.lg, vertical=Spacing.md),
            ),
        ],
        spacing=Spacing.md,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
    )
