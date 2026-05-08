"""Reusable background layers for premium auth/landing surfaces."""

from __future__ import annotations

import flet as ft

from ui.themes.app_theme import Colors


def subtle_grid_layer(*, opacity: float = 0.045) -> ft.Control:
    """Low-noise grid texture for futuristic workspace feel."""
    return ft.Container(
        expand=True,
        opacity=opacity,
        content=ft.Column(
            expand=True,
            spacing=0,
            controls=[
                ft.Container(
                    expand=True,
                    border=ft.border.all(1, ft.colors.with_opacity(0.55, "#475569")),
                    border_radius=0,
                )
            ],
        ),
    )


def ambient_orb(
    *,
    size: int,
    color_hex: str,
    align_left: bool = False,
    align_top: bool = False,
    x_offset: int = -120,
    y_offset: int = -120,
    opacity: float = 0.2,
) -> ft.Control:
    return ft.Container(
        width=size,
        height=size,
        border_radius=999,
        gradient=ft.RadialGradient(
            center=ft.alignment.center,
            radius=0.9,
            colors=[
                ft.colors.with_opacity(opacity, color_hex),
                "#02061700",
            ],
        ),
        left=x_offset if align_left else None,
        right=None if align_left else x_offset,
        top=y_offset if align_top else None,
        bottom=None if align_top else y_offset,
    )


def shared_auth_backdrop() -> ft.Control:
    """Unified page background for both hero and auth panels."""
    return ft.Container(
        expand=True,
        gradient=ft.LinearGradient(
            begin=ft.alignment.top_left,
            end=ft.alignment.bottom_right,
            colors=[Colors.background, "#081224", Colors.surface],
        ),
    )
