"""Design tokens and theme builders.

This is the single source of truth for color, spacing, radii, and
typography. Importing modules should never hard-code hex values; they
should pull from ``Colors``, ``Spacing``, etc.
"""

from __future__ import annotations

import flet as ft


class Colors:
    """Brand-aligned color tokens (dark, premium, futuristic)."""

    background = "#020617"
    surface = "#0f172a"
    surface_2 = "#111827"
    surface_3 = "#1a2238"

    primary = "#8b5cf6"
    primary_soft = "#a78bfa"
    primary_glow = "#c4b5fd"
    accent_cyan = "#22d3ee"
    accent_pink = "#f472b6"

    success = "#34d399"
    warning = "#fbbf24"
    danger = "#f87171"

    text_primary = "#f8fafc"
    text_secondary = "#94a3b8"
    text_muted = "#64748b"

    border = "#1e293b"
    border_strong = "#334155"

    glass = "#0f172a"  # base for translucent surfaces
    glass_border = "#1e293b"


class Spacing:
    xs = 4
    sm = 8
    md = 12
    lg = 16
    xl = 24
    xxl = 32
    xxxl = 48


class Radii:
    sm = 8
    md = 12
    lg = 16
    xl = 22
    pill = 999


class Typography:
    family = "Inter, Segoe UI, system-ui, sans-serif"

    @staticmethod
    def display(size: int = 32, weight: ft.FontWeight = ft.FontWeight.W_700) -> ft.TextStyle:
        return ft.TextStyle(
            size=size, weight=weight, color=Colors.text_primary, letter_spacing=-0.5
        )

    @staticmethod
    def heading(size: int = 22, weight: ft.FontWeight = ft.FontWeight.W_700) -> ft.TextStyle:
        return ft.TextStyle(size=size, weight=weight, color=Colors.text_primary)

    @staticmethod
    def subheading(size: int = 16) -> ft.TextStyle:
        return ft.TextStyle(size=size, weight=ft.FontWeight.W_600, color=Colors.text_primary)

    @staticmethod
    def body(size: int = 14, color: str = Colors.text_secondary) -> ft.TextStyle:
        return ft.TextStyle(size=size, color=color, height=1.5)

    @staticmethod
    def caption() -> ft.TextStyle:
        return ft.TextStyle(size=12, color=Colors.text_muted, letter_spacing=0.4)

    @staticmethod
    def code() -> ft.TextStyle:
        return ft.TextStyle(size=13, color=Colors.text_primary, font_family="Consolas, monospace")


class Shadows:
    card = ft.BoxShadow(
        spread_radius=0, blur_radius=24, color="#00000066",
        offset=ft.Offset(0, 12),
    )
    soft = ft.BoxShadow(
        spread_radius=0, blur_radius=18, color="#00000040",
        offset=ft.Offset(0, 8),
    )
    glow = ft.BoxShadow(
        spread_radius=0, blur_radius=30, color="#8b5cf655",
        offset=ft.Offset(0, 0),
    )


class Gradients:
    @staticmethod
    def primary() -> ft.LinearGradient:
        return ft.LinearGradient(
            begin=ft.alignment.top_left,
            end=ft.alignment.bottom_right,
            colors=[Colors.primary, Colors.accent_cyan],
        )

    @staticmethod
    def hero() -> ft.LinearGradient:
        return ft.LinearGradient(
            begin=ft.alignment.top_left,
            end=ft.alignment.bottom_right,
            colors=["#1e1b4b", "#312e81", "#0f172a"],
        )

    @staticmethod
    def card_subtle() -> ft.LinearGradient:
        return ft.LinearGradient(
            begin=ft.alignment.top_left,
            end=ft.alignment.bottom_right,
            colors=["#111827", "#0f172a"],
        )

    @staticmethod
    def aura() -> ft.RadialGradient:
        return ft.RadialGradient(
            center=ft.alignment.center,
            radius=1.4,
            colors=["#8b5cf633", "#020617"],
        )


def build_flet_theme() -> ft.Theme:
    return ft.Theme(
        color_scheme_seed=Colors.primary,
        color_scheme=ft.ColorScheme(
            primary=Colors.primary,
            on_primary=Colors.text_primary,
            secondary=Colors.accent_cyan,
            background=Colors.background,
            on_background=Colors.text_primary,
            surface=Colors.surface,
            on_surface=Colors.text_primary,
            error=Colors.danger,
        ),
        font_family="Segoe UI",
        use_material3=True,
        scrollbar_theme=ft.ScrollbarTheme(
            track_color=ft.colors.with_opacity(0.0, Colors.text_muted),
            thumb_color=ft.colors.with_opacity(0.4, Colors.text_muted),
            thickness=8,
            radius=4,
        ),
    )
