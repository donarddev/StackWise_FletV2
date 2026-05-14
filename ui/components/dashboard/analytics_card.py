"""Dashboard analytics card — minimal Laravel-style stat tiles."""

from __future__ import annotations

from typing import Any, Mapping

import flet as ft

from ui.components.dashboard.glass_tokens import dashboard_glass_tokens
from ui.themes.app_theme import Radii, Spacing
from ui.theme import card_box_shadow, display_style, text_style

_STAT_CARD_HEIGHT = 158
_PAD = 20


def dashboard_analytics_card(
    *,
    title: str,
    value: str | int | float,
    description: str,
    icon: str | None = None,
    accent_color: str,
    theme: Mapping[str, Any],
) -> ft.Control:
    """One consistent minimal glass card; ``icon`` / ``accent_color`` kept for API compatibility."""

    _ = (icon, accent_color)

    if isinstance(value, float):
        display_value = f"{value:.0f}" if value > 0 else "—"
    else:
        display_value = str(value) if value else "—"

    g = dashboard_glass_tokens(theme)
    card_ref = ft.Ref[ft.Container]()

    rest_bg = g["card_bg"]
    hover_bg = g["card_hover"]

    def _rest_shadow() -> list[ft.BoxShadow]:
        return [
            card_box_shadow(theme),
            ft.BoxShadow(
                spread_radius=0,
                blur_radius=12,
                color=ft.colors.with_opacity(0.1, g["teal"]),
                offset=ft.Offset(0, 3),
            ),
        ]

    def _hover_shadow() -> list[ft.BoxShadow]:
        return [
            card_box_shadow(theme),
            ft.BoxShadow(
                spread_radius=0,
                blur_radius=18,
                color=ft.colors.with_opacity(0.18, g["teal"]),
                offset=ft.Offset(0, 5),
            ),
        ]

    def _on_hover(e: ft.ControlEvent) -> None:
        hovered = str(getattr(e, "data", "")).lower() == "true"
        card = card_ref.current
        if card is None:
            return
        if hovered:
            card.bgcolor = hover_bg
            card.border = ft.border.all(1, ft.colors.with_opacity(0.52, g["teal"]))
            card.shadow = _hover_shadow()
        else:
            card.bgcolor = rest_bg
            card.border = ft.border.all(1, g["card_border"])
            card.shadow = _rest_shadow()
        if card.page:
            card.update()

    inner = ft.Column(
        spacing=Spacing.sm,
        tight=True,
        controls=[
            ft.Text(
                title,
                style=text_style(theme, size=11, weight=ft.FontWeight.W_600, color_key="text_muted"),
            ),
            ft.Text(
                display_value,
                style=display_style(theme, size=27),
            ),
            ft.Text(
                description,
                style=text_style(theme, size=11.5, height=1.42, color_key="text_secondary"),
                max_lines=3,
            ),
        ],
    )

    return ft.Container(
        ref=card_ref,
        height=_STAT_CARD_HEIGHT,
        padding=ft.padding.all(_PAD),
        border_radius=Radii.lg,
        bgcolor=rest_bg,
        border=ft.border.all(1, g["card_border"]),
        shadow=_rest_shadow(),
        content=inner,
        on_hover=_on_hover,
        animate=ft.Animation(160, ft.AnimationCurve.EASE_OUT),
    )
