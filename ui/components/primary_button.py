"""Brand buttons — primary (gradient) and secondary (outline)."""

from __future__ import annotations

from typing import Callable, Optional

import flet as ft

from ui.themes.app_theme import Colors, Radii, Spacing


def primary_button(
    text: str,
    on_click: Callable[[ft.ControlEvent], None],
    *,
    icon: Optional[str] = None,
    expand: bool | int = False,
    width: Optional[int] = None,
    height: int = 46,
    disabled: bool = False,
    ref: Optional[ft.Ref[ft.Container]] = None,
) -> ft.Container:
    """Pill-shaped, gradient-filled, primary action button."""
    label = ft.Row(
        controls=[
            *( [ft.Icon(icon, color=Colors.text_primary, size=18)] if icon else []),
            ft.Text(text, size=14, weight=ft.FontWeight.W_600, color=Colors.text_primary),
        ],
        spacing=Spacing.sm,
        alignment=ft.MainAxisAlignment.CENTER,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
        tight=True,
    )

    container = ft.Container(
        ref=ref,
        content=label,
        gradient=ft.LinearGradient(
            begin=ft.alignment.top_left,
            end=ft.alignment.bottom_right,
            colors=[Colors.primary, "#6366f1"],
        ),
        border_radius=Radii.md,
        padding=ft.padding.symmetric(horizontal=22, vertical=12),
        height=height,
        ink=True,
        # Store original handler so controllers can toggle busy/disabled state
        # without losing the click callback permanently.
        data={"on_click": on_click},
        on_click=None if disabled else on_click,
        opacity=0.55 if disabled else 1.0,
        animate_opacity=140,
        animate_scale=ft.Animation(160, ft.AnimationCurve.EASE_OUT),
        scale=ft.Scale(1),
        shadow=ft.BoxShadow(
            spread_radius=0, blur_radius=22, color="#8b5cf655",
            offset=ft.Offset(0, 6),
        ),
        expand=expand,
        width=width,
        alignment=ft.alignment.center,
    )
    return container


def secondary_button(
    text: str,
    on_click: Callable[[ft.ControlEvent], None],
    *,
    icon: Optional[str] = None,
    expand: bool | int = False,
    width: Optional[int] = None,
    height: int = 46,
) -> ft.Container:
    """Outline ghost button for secondary actions."""
    label = ft.Row(
        controls=[
            *( [ft.Icon(icon, color=Colors.text_primary, size=18)] if icon else []),
            ft.Text(text, size=14, weight=ft.FontWeight.W_600, color=Colors.text_primary),
        ],
        spacing=Spacing.sm,
        alignment=ft.MainAxisAlignment.CENTER,
        tight=True,
    )
    return ft.Container(
        content=label,
        border=ft.border.all(1, Colors.border_strong),
        bgcolor=Colors.surface_2,
        border_radius=Radii.md,
        padding=ft.padding.symmetric(horizontal=22, vertical=12),
        height=height,
        ink=True,
        on_click=on_click,
        expand=expand,
        width=width,
        alignment=ft.alignment.center,
    )


def text_link(text: str, on_click: Callable[[ft.ControlEvent], None]) -> ft.Container:
    return ft.Container(
        content=ft.Text(text, size=13, weight=ft.FontWeight.W_600, color=Colors.primary_soft),
        on_click=on_click,
        ink=False,
        padding=ft.padding.symmetric(horizontal=4, vertical=4),
    )
