"""LearningCard — entry tile in the Learning Hub."""

from __future__ import annotations

from typing import Callable

import flet as ft

from app.models.learning_article import LearningArticle
from ui.components.glass_card import glass_card
from ui.themes.app_theme import Colors, Radii, Spacing, Typography


def learning_card(
    article: LearningArticle,
    *,
    on_open: Callable[[LearningArticle], None],
) -> ft.Control:
    accent = {
        "Languages": Colors.primary,
        "Frameworks": Colors.accent_cyan,
        "SDLC": Colors.accent_pink,
        "Concepts": Colors.success,
    }.get(article.category, Colors.primary)

    pill = ft.Container(
        bgcolor=ft.colors.with_opacity(0.14, accent),
        border=ft.border.all(1, ft.colors.with_opacity(0.4, accent)),
        border_radius=Radii.pill,
        padding=ft.padding.symmetric(horizontal=10, vertical=4),
        content=ft.Text(
            article.category.upper(),
            style=ft.TextStyle(
                size=10.5, weight=ft.FontWeight.W_700,
                color=accent, letter_spacing=1.4,
            ),
        ),
    )

    tags = ft.Row(
        wrap=True, spacing=6, run_spacing=6,
        controls=[
            ft.Container(
                bgcolor=Colors.surface_3,
                border_radius=Radii.pill,
                padding=ft.padding.symmetric(horizontal=8, vertical=3),
                content=ft.Text(t, size=10.5, color=Colors.text_secondary),
            )
            for t in article.tags
        ],
    )

    body = ft.Column(
        spacing=Spacing.md,
        controls=[
            ft.Row(controls=[pill]),
            ft.Text(article.title, style=Typography.subheading(size=17)),
            ft.Text(article.summary, style=Typography.body()),
            tags,
            ft.Container(expand=1),
            ft.Row(
                controls=[
                    ft.Text("Read article", size=12, weight=ft.FontWeight.W_700, color=accent),
                    ft.Icon(ft.icons.ARROW_FORWARD, size=14, color=accent),
                ],
                spacing=Spacing.xs,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
        ],
        expand=True,
    )

    card = glass_card(body, expand=True, padding=Spacing.lg)
    card.on_click = lambda _e: on_open(article)
    card.ink = True
    return card
