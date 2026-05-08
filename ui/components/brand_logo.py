"""BrandLogo — renders a premium icon + wordmark + subtitle."""

from __future__ import annotations

import flet as ft

from app.utils.constants import BRAND_INITIALS, BRAND_NAME
from ui.themes.app_theme import Colors, Gradients, Radii, Spacing, Typography


def brand_logo(
    *,
    subtitle: str = "AI-powered decision support",
    compact: bool = False,
    icon_size: int | None = None,
    title_size: int | None = None,
    subtitle_size: int | None = None,
    show_subtitle: bool = True,
) -> ft.Control:
    """Reusable branding block (icon + wordmark + subtitle).

    We intentionally render the wordmark as text so branding never becomes
    "icon-only" even if the provided logo asset is only an icon.
    """

    icon_size = icon_size or (34 if not compact else 30)
    title_size = title_size or (18 if not compact else 16)
    subtitle_size = subtitle_size or (12 if not compact else 11)
    icon = brand_icon(size=icon_size, radius=12)

    wordmark = ft.Column(
        spacing=2,
        tight=True,
        controls=[
            ft.Text(
                BRAND_NAME,
                size=title_size,
                weight=ft.FontWeight.W_800,
                color=Colors.text_primary,
            ),
            *(
                [
                    ft.Text(
                        subtitle,
                        size=subtitle_size,
                        color=Colors.text_secondary,
                    )
                ]
                if show_subtitle
                else []
            ),
        ],
    )

    return ft.Container(
        padding=ft.padding.symmetric(horizontal=12, vertical=10),
        bgcolor=ft.colors.with_opacity(0.55, Colors.surface),
        border=ft.border.all(1, ft.colors.with_opacity(0.75, Colors.border)),
        border_radius=Radii.xl,
        content=ft.Row(
            spacing=Spacing.md,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[icon, wordmark],
        ),
    )


def brand_icon(*, size: int = 34, radius: int = 12) -> ft.Control:
    fallback_mark = ft.Container(
        width=size,
        height=size,
        border_radius=radius,
        gradient=Gradients.primary(),
        alignment=ft.alignment.center,
        content=ft.Text(
            BRAND_INITIALS,
            size=max(13, size // 2 - 3),
            weight=ft.FontWeight.W_800,
            color=Colors.text_primary,
        ),
    )
    return ft.Container(
        width=size,
        height=size,
        border_radius=radius,
        bgcolor=ft.colors.with_opacity(0.30, Colors.surface),
        border=ft.border.all(1, ft.colors.with_opacity(0.75, Colors.border)),
        alignment=ft.alignment.center,
        content=ft.Image(
            src="images/StackWise_Logo.png",
            width=size - 6,
            height=size - 6,
            fit=ft.ImageFit.CONTAIN,
            error_content=ft.Image(
                src="images/StackWise_Logo.svg",
                width=size - 4,
                height=size - 4,
                fit=ft.ImageFit.CONTAIN,
                error_content=fallback_mark,
            ),
        ),
    )

