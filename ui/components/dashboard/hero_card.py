"""Dashboard workspace welcome hero card."""

from __future__ import annotations

from typing import Any, Callable, Mapping

import flet as ft

from ui.components.dashboard.glass_tokens import dashboard_glass_tokens
from ui.components.primary_button import primary_button, secondary_button
from ui.themes.app_theme import Radii, Spacing
from ui.theme import caption_style, card_box_shadow, display_style, text_style


def dashboard_hero_card(
    *,
    user_name: str,
    on_new_recommendation: Callable[[ft.ControlEvent], None],
    on_view_history: Callable[[ft.ControlEvent], None],
    theme: Mapping[str, Any],
) -> ft.Control:
    """Minimal glass hero: greeting and actions (Laravel-style calm layout)."""

    g = dashboard_glass_tokens(theme)
    first_name = user_name.split()[0] if user_name else "User"
    teal = theme["accent_2"]

    hero_ref = ft.Ref[ft.Container]()

    def _on_hero_hover(e: ft.ControlEvent) -> None:
        box = hero_ref.current
        if box is None:
            return
        hovered = str(getattr(e, "data", "")).lower() == "true"
        if hovered:
            box.bgcolor = g["card_hover"]
            box.border = ft.border.all(1, ft.colors.with_opacity(0.5, g["teal"]))
            box.shadow = [
                card_box_shadow(theme),
                ft.BoxShadow(
                    spread_radius=0,
                    blur_radius=16,
                    color=ft.colors.with_opacity(0.16, g["teal"]),
                    offset=ft.Offset(0, 5),
                ),
            ]
        else:
            box.bgcolor = g["card_bg"]
            box.border = ft.border.all(1, g["card_border"])
            box.shadow = [
                card_box_shadow(theme),
                ft.BoxShadow(
                    spread_radius=0,
                    blur_radius=14,
                    color=ft.colors.with_opacity(0.1, g["teal"]),
                    offset=ft.Offset(0, 4),
                ),
            ]
        if box.page:
            box.update()

    hero_content = ft.Column(
        spacing=Spacing.md,
        horizontal_alignment=ft.CrossAxisAlignment.START,
        controls=[
            ft.Container(
                padding=ft.padding.symmetric(horizontal=Spacing.md, vertical=3),
                bgcolor=ft.colors.with_opacity(0.12, teal),
                border_radius=Radii.pill,
                border=ft.border.all(1, ft.colors.with_opacity(0.35, teal)),
                content=ft.Text(
                    "WORKSPACE",
                    style=caption_style(theme, size=11),
                    color=teal,
                ),
            ),
            ft.Text(
                f"Welcome back, {first_name}.",
                style=display_style(theme, size=26),
            ),
            ft.Text(
                "Your personalized StackWise AI workspace — recent decisions, saved "
                "recommendations, and quick actions in one place.",
                style=text_style(theme, size=14, height=1.45, color_key="text_secondary"),
                max_lines=3,
            ),
            ft.Row(
                spacing=Spacing.md,
                alignment=ft.MainAxisAlignment.START,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                wrap=True,
                run_spacing=Spacing.md,
                controls=[
                    primary_button(
                        "Generate recommendation",
                        on_click=on_new_recommendation,
                        icon="auto_awesome",
                        theme=theme,
                        mint_fill=True,
                        width=272,
                        border_radius=Radii.pill,
                    ),
                    secondary_button(
                        "View history",
                        on_click=on_view_history,
                        icon="history",
                        theme=theme,
                        height=44,
                        width=168,
                        border_radius=Radii.pill,
                        bgcolor=ft.colors.with_opacity(0.28, theme["surface_2"]),
                        border_color=ft.colors.with_opacity(0.72, g["card_border"]),
                    ),
                ],
            ),
        ],
    )

    return ft.Container(
        ref=hero_ref,
        padding=ft.padding.symmetric(horizontal=28, vertical=26),
        border_radius=Radii.lg,
        bgcolor=g["card_bg"],
        border=ft.border.all(1, g["card_border"]),
        shadow=[
            card_box_shadow(theme),
            ft.BoxShadow(
                spread_radius=0,
                blur_radius=14,
                color=ft.colors.with_opacity(0.1, g["teal"]),
                offset=ft.Offset(0, 4),
            ),
        ],
        content=hero_content,
        on_hover=_on_hero_hover,
        animate=ft.Animation(160, ft.AnimationCurve.EASE_OUT),
    )
