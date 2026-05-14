"""GlassCard — a futuristic glass-morphism container.

Used as the universal surface across the app. Supports optional gradient
border, glow, and hover lift.
"""

from __future__ import annotations

from typing import Any, Mapping, Optional

import flet as ft

from ui.animations.transitions import Motion
from ui.themes.app_theme import Colors, Radii, Shadows, Spacing
from ui.theme import card_box_shadow


def glass_card(
    content: ft.Control,
    *,
    padding: int | ft.Padding = Spacing.xl,
    radius: int = Radii.lg,
    bgcolor: str = Colors.surface_2,
    border_color: str = Colors.border,
    glow: bool = False,
    expand: bool | int = False,
    width: Optional[int] = None,
    height: Optional[int] = None,
    theme: Optional[Mapping[str, Any]] = None,
    card_bg_override: Optional[str] = None,
    border_color_override: Optional[str] = None,
) -> ft.Container:
    if theme is not None:
        bg = card_bg_override if card_bg_override is not None else theme["card_bg"]
        bd = border_color_override if border_color_override is not None else theme["border"]
        if glow:
            sh = ft.BoxShadow(
                spread_radius=0,
                blur_radius=26,
                color=ft.colors.with_opacity(0.32, theme["accent"]),
                offset=ft.Offset(0, 10),
            )
        else:
            sh = card_box_shadow(theme)
    else:
        bg = bgcolor
        bd = border_color
        sh = Shadows.glow if glow else Shadows.card
    return ft.Container(
        content=content,
        padding=padding,
        bgcolor=bg,
        border_radius=radius,
        border=ft.border.all(1, bd),
        shadow=sh,
        expand=expand,
        width=width,
        height=height,
        animate=Motion.fade(),
    )


def gradient_card(
    content: ft.Control,
    *,
    padding: int | ft.Padding = Spacing.xl,
    radius: int = Radii.lg,
    expand: bool | int = False,
    width: Optional[int] = None,
    height: Optional[int] = None,
) -> ft.Container:
    return ft.Container(
        content=content,
        padding=padding,
        gradient=ft.LinearGradient(
            begin=ft.alignment.top_left,
            end=ft.alignment.bottom_right,
            colors=["#1e1b4b", "#0f172a"],
        ),
        border_radius=radius,
        border=ft.border.all(1, Colors.border),
        shadow=Shadows.soft,
        expand=expand,
        width=width,
        height=height,
    )
