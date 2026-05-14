"""Brand buttons — primary (gradient) and secondary (outline)."""

from __future__ import annotations

from typing import Any, Callable, Mapping, Optional

import flet as ft

from ui.themes.app_theme import Colors, Radii, Spacing
from ui.theme import primary_gradient


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
    theme: Optional[Mapping[str, Any]] = None,
    mint_fill: bool = False,
    border_radius: Optional[float] = None,
) -> ft.Container:
    """Pill-shaped primary action. ``mint_fill`` uses a calm teal fill + soft shadow (dashboard)."""
    if theme is not None and mint_fill:
        fg = "#061016"
        t2 = theme["accent_2"]
        grad = ft.LinearGradient(
            begin=ft.alignment.top_left,
            end=ft.alignment.bottom_right,
            colors=[t2, ft.colors.with_opacity(0.88, t2)],
        )
        sh_color = ft.colors.with_opacity(0.22, t2)
    else:
        fg = theme["on_gradient"] if theme is not None else Colors.text_primary
        grad = primary_gradient(theme) if theme is not None else ft.LinearGradient(
            begin=ft.alignment.top_left,
            end=ft.alignment.bottom_right,
            colors=[Colors.primary, "#6366f1"],
        )
        sh_color = theme["button_shadow"] if theme is not None else "#8b5cf655"
    label = ft.Row(
        controls=[
            *( [ft.Icon(icon, color=fg, size=18)] if icon else []),
            ft.Text(text, size=14, weight=ft.FontWeight.W_600, color=fg),
        ],
        spacing=Spacing.sm,
        alignment=ft.MainAxisAlignment.CENTER,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
        tight=True,
    )

    radius = border_radius if border_radius is not None else Radii.md
    container = ft.Container(
        ref=ref,
        content=label,
        gradient=grad,
        border_radius=radius,
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
            spread_radius=0,
            blur_radius=14 if (theme is not None and mint_fill) else 22,
            color=sh_color,
            offset=ft.Offset(0, 3 if (theme is not None and mint_fill) else 6),
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
    theme: Optional[Mapping[str, Any]] = None,
    bgcolor: Optional[str] = None,
    border_color: Optional[str] = None,
    border_radius: Optional[float] = None,
    hover_border_color: Optional[str] = None,
    ref: Optional[ft.Ref[ft.Container]] = None,
) -> ft.Container:
    """Outline ghost button for secondary actions."""
    fg = theme["text"] if theme is not None else Colors.text_primary
    border_c = border_color if border_color is not None else (
        theme["border_strong"] if theme is not None else Colors.border_strong
    )
    bg_s = bgcolor if bgcolor is not None else (
        theme["secondary_surface"] if theme is not None else Colors.surface_2
    )
    label = ft.Row(
        controls=[
            *( [ft.Icon(icon, color=fg, size=18)] if icon else []),
            ft.Text(text, size=14, weight=ft.FontWeight.W_600, color=fg),
        ],
        spacing=Spacing.sm,
        alignment=ft.MainAxisAlignment.CENTER,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
        tight=True,
    )
    radius = border_radius if border_radius is not None else Radii.md

    def _on_hover(e: ft.ControlEvent) -> None:
        if hover_border_color is None:
            return
        box = btn_ref.current
        if box is None:
            return
        hovered = str(getattr(e, "data", "")).lower() == "true"
        box.border = ft.border.all(1, hover_border_color if hovered else border_c)
        if box.page:
            box.update()

    btn_ref = ref if ref is not None else ft.Ref[ft.Container]()
    return ft.Container(
        ref=btn_ref,
        content=label,
        border=ft.border.all(1, border_c),
        bgcolor=bg_s,
        border_radius=radius,
        padding=ft.padding.symmetric(horizontal=22, vertical=12),
        height=height,
        ink=True,
        on_click=on_click,
        on_hover=_on_hover if hover_border_color is not None else None,
        expand=expand,
        width=width,
        alignment=ft.alignment.center,
    )


def text_link(
    text: str,
    on_click: Callable[[ft.ControlEvent], None],
    *,
    theme: Optional[Mapping[str, Any]] = None,
) -> ft.Container:
    fg = theme["accent_soft"] if theme is not None else Colors.primary_soft
    return ft.Container(
        content=ft.Text(text, size=13, weight=ft.FontWeight.W_600, color=fg),
        on_click=on_click,
        ink=False,
        padding=ft.padding.symmetric(horizontal=4, vertical=4),
    )
