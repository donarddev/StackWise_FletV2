"""GlassCard — a futuristic glass-morphism container.

Used as the universal surface across the app. Supports optional gradient
border, glow, and hover lift.
"""

from __future__ import annotations

from typing import Optional

import flet as ft

from ui.animations.transitions import Motion
from ui.themes.app_theme import Colors, Radii, Shadows, Spacing


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
) -> ft.Container:
    return ft.Container(
        content=content,
        padding=padding,
        bgcolor=bgcolor,
        border_radius=radius,
        border=ft.border.all(1, border_color),
        shadow=Shadows.glow if glow else Shadows.card,
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
