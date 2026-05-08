"""ArticleDialog — Learning Hub reading view."""

from __future__ import annotations

import flet as ft

from app.models.learning_article import LearningArticle
from ui.themes.app_theme import Colors, Radii, Spacing, Typography


def build_article_dialog(article: LearningArticle, *, on_close) -> ft.AlertDialog:
    return ft.AlertDialog(
        modal=True,
        bgcolor=Colors.surface,
        shape=ft.RoundedRectangleBorder(radius=Radii.lg),
        content=ft.Container(
            width=720,
            content=ft.Column(
                spacing=Spacing.md,
                scroll=ft.ScrollMode.ADAPTIVE,
                height=520,
                controls=[
                    ft.Text(
                        article.category.upper(),
                        style=ft.TextStyle(
                            size=11, weight=ft.FontWeight.W_700,
                            color=Colors.primary_glow, letter_spacing=1.4,
                        ),
                    ),
                    ft.Text(article.title, style=Typography.heading(size=22)),
                    ft.Text(article.summary, style=Typography.body(size=14)),
                    ft.Divider(color=Colors.border, height=1),
                    ft.Markdown(
                        value=article.content,
                        selectable=True,
                        extension_set=ft.MarkdownExtensionSet.GITHUB_FLAVORED,
                        code_theme="atom-one-dark",
                    ),
                ],
            ),
        ),
        actions=[ft.TextButton("Close", on_click=on_close)],
    )
