"""Light/dark theme tokens for the authenticated workspace (Phase 1).

Single source for dashboard shell + dashboard page surfaces. Public routes
continue to use ``ui.themes.app_theme`` until a later phase.
"""

from __future__ import annotations

from typing import Any, Mapping

import flet as ft

THEME_MODE_DARK = "dark"
THEME_MODE_LIGHT = "light"
_SESSION_KEY = "theme_mode"


def _read_stored_mode(page: ft.Page) -> str | None:
    try:
        v = page.client_storage.get(_SESSION_KEY)
        if v in (THEME_MODE_DARK, THEME_MODE_LIGHT):
            return v
    except Exception:
        pass
    v = getattr(page, "_stackwise_theme_mode", None)
    if v in (THEME_MODE_DARK, THEME_MODE_LIGHT):
        return v
    return None


def _write_mode(page: ft.Page, mode: str) -> None:
    setattr(page, "_stackwise_theme_mode", mode)
    try:
        page.client_storage.set(_SESSION_KEY, mode)
    except Exception:
        pass


def get_theme_mode(page: ft.Page) -> str:
    """Return ``dark`` or ``light``. Defaults to dark."""
    m = _read_stored_mode(page)
    return m if m is not None else THEME_MODE_DARK


def is_dark_mode(page: ft.Page) -> bool:
    return get_theme_mode(page) == THEME_MODE_DARK


def set_theme_mode(page: ft.Page, mode: str) -> None:
    if mode not in (THEME_MODE_DARK, THEME_MODE_LIGHT):
        mode = THEME_MODE_DARK
    _write_mode(page, mode)


def sync_page_workspace_chrome(page: ft.Page, theme: Mapping[str, Any]) -> None:
    """Align Flet page chrome with stored workspace mode (auth shell only)."""
    dark = is_dark_mode(page)
    page.theme_mode = ft.ThemeMode.DARK if dark else ft.ThemeMode.LIGHT
    page.bgcolor = theme["page_bg"]
    try:
        if page.window:
            page.window.bgcolor = theme["page_bg"]
    except Exception:
        pass


def toggle_theme_mode(page: ft.Page) -> str:
    """Flip theme, persist, sync Flet page chrome. Returns new mode."""
    nxt = THEME_MODE_LIGHT if is_dark_mode(page) else THEME_MODE_DARK
    set_theme_mode(page, nxt)
    t = get_theme(nxt == THEME_MODE_DARK)
    sync_page_workspace_chrome(page, t)
    try:
        from app.core.theme_persistence import persist_user_theme_mode

        persist_user_theme_mode(page)
    except Exception:
        pass
    return nxt


def hydrate_theme_after_login(page: ft.Page, user: Any) -> None:
    """Apply saved DB theme after login; if none, keep client_storage value (or default dark)."""
    m = getattr(user, "theme_mode", None)
    if m in (THEME_MODE_DARK, THEME_MODE_LIGHT):
        set_theme_mode(page, m)
        sync_page_workspace_chrome(page, get_theme(m == THEME_MODE_DARK))


def get_theme(is_dark: bool) -> dict[str, Any]:
    """Return token dict for the given mode."""
    return DARK_THEME if is_dark else LIGHT_THEME


DARK_THEME: dict[str, Any] = {
    "page_bg": "#020617",
    "surface": "#0f172a",
    "surface_2": "#111827",
    "surface_3": "#1a2238",
    "glass": "#0f172a",
    "card_bg": "#111827",
    "border": "#1e293b",
    "border_strong": "#334155",
    "text": "#f8fafc",
    "text_secondary": "#94a3b8",
    "text_muted": "#64748b",
    "accent": "#8b5cf6",
    "accent_soft": "#a78bfa",
    "accent_glow": "#c4b5fd",
    "accent_2": "#22d3ee",
    "accent_pink": "#f472b6",
    "success": "#34d399",
    "warning": "#fbbf24",
    "danger": "#f87171",
    "button_gradient_end": "#6366f1",
    "button_shadow": "#8b5cf655",
    "hover": "rgba(139,92,246,0.12)",
    "sidebar_bg": "#0f172a",
    "topbar_bg_base": "#0f172a",
    "topbar_bg_alpha": 0.65,
    "nav_selected_alpha": 0.22,
    "nav_hover_selected_alpha": 0.24,
    "nav_hover_alpha": 0.12,
    "backdrop_colors": ["#020617", "#081224", "#0f172a"],
    "grid_line": "#475569",
    "grid_layer_opacity": 0.04,
    "grid_cell_opacity": 0.55,
    "orb_fade": "#02061700",
    "orb_primary_opacity": 0.12,
    "orb_cyan_opacity": 0.10,
    "card_shadow_color": "#00000066",
    "card_shadow_blur": 24.0,
    "card_shadow_offset_y": 12.0,
    "card_shadow_spread": 0.0,
    "secondary_surface": "#111827",
    "table_header_tint": 0.08,
    "table_header_border": 0.2,
    "confidence_high": "#34d399",
    "confidence_mid": "#fbbf24",
    "confidence_low": "#f87171",
    "on_gradient": "#ffffff",
    "confidence_band_mid": "#8b5cf6",
    "markdown_code_theme": "atom-one-dark",
    "data_row_selected": "#1c1538",
    "data_row_selected_hover": "#2a1f4a",
    "data_row_alt": "#111a2e",
    "data_row_even": "#111827",
    "data_row_hover": "#172036",
    "datatable_heading_bg": "#1a2238",
    "datatable_divider": "#334155",
    "history_surface_grad_start": "#111827",
    "history_surface_grad_end": "#0f172a",
    "history_surface_border": "#334155",
    "chat_panel_bg": "#111827",
    "chat_composer_bg": "#0f172a",
    "learning_chip_limit_fg": "#fef3c7",
    "learning_chip_trade_fg": "#fecaca",
    "learning_chip_diff_fg": "#e9d5ff",
    "learning_chip_best_fg": "#ccfbf1",
}

LIGHT_THEME: dict[str, Any] = {
    "page_bg": "#f6f8fb",
    "surface": "#ffffff",
    "surface_2": "rgba(255,255,255,0.82)",
    "surface_3": "#f1f5f9",
    "glass": "rgba(255,255,255,0.78)",
    "card_bg": "rgba(255,255,255,0.78)",
    "border": "#dbe3ef",
    "border_strong": "rgba(15,23,42,0.14)",
    "text": "#0f172a",
    "text_secondary": "#64748b",
    "text_muted": "#94a3b8",
    "accent": "#7c3aed",
    "accent_soft": "#8b5cf6",
    "accent_glow": "#6d28d9",
    "accent_2": "#0f766e",
    "accent_pink": "#db2777",
    "success": "#059669",
    "warning": "#d97706",
    "danger": "#dc2626",
    "button_gradient_end": "#14b8a6",
    "button_shadow": "rgba(15,118,110,0.35)",
    "hover": "rgba(15,23,42,0.06)",
    "sidebar_bg": "rgba(255,255,255,0.92)",
    "topbar_bg_base": "#ffffff",
    "topbar_bg_alpha": 0.88,
    "nav_selected_alpha": 0.14,
    "nav_hover_selected_alpha": 0.18,
    "nav_hover_alpha": 0.08,
    "backdrop_colors": ["#f6f8fb", "#eef2ff", "#ecfeff"],
    "grid_line": "#94a3b8",
    "grid_layer_opacity": 0.06,
    "grid_cell_opacity": 0.22,
    "orb_fade": "#f6f8fb00",
    "orb_primary_opacity": 0.10,
    "orb_cyan_opacity": 0.08,
    "card_shadow_color": "rgba(15,23,42,0.08)",
    "card_shadow_blur": 28.0,
    "card_shadow_offset_y": 14.0,
    "card_shadow_spread": 0.0,
    "secondary_surface": "rgba(248,250,252,0.95)",
    "table_header_tint": 0.10,
    "table_header_border": 0.35,
    "confidence_high": "#059669",
    "confidence_mid": "#d97706",
    "confidence_low": "#dc2626",
    "on_gradient": "#ffffff",
    "confidence_band_mid": "#7c3aed",
    "markdown_code_theme": "default",
    "data_row_selected": "rgba(124, 58, 237, 0.14)",
    "data_row_selected_hover": "rgba(124, 58, 237, 0.22)",
    "data_row_alt": "#f1f5f9",
    "data_row_even": "rgba(255,255,255,0.92)",
    "data_row_hover": "rgba(15, 23, 42, 0.06)",
    "datatable_heading_bg": "#e8eef7",
    "datatable_divider": "rgba(15, 23, 42, 0.12)",
    "history_surface_grad_start": "#ffffff",
    "history_surface_grad_end": "#f0fdfa",
    "history_surface_border": "rgba(15, 23, 42, 0.12)",
    "chat_panel_bg": "rgba(255,255,255,0.82)",
    "chat_composer_bg": "#ffffff",
    "learning_chip_limit_fg": "#78350f",
    "learning_chip_trade_fg": "#991b1b",
    "learning_chip_diff_fg": "#5b21b6",
    "learning_chip_best_fg": "#0f766e",
}


def subheading_style(theme: Mapping[str, Any], *, size: float = 16) -> ft.TextStyle:
    return ft.TextStyle(size=size, weight=ft.FontWeight.W_600, color=theme["text"])


def text_style(
    theme: Mapping[str, Any],
    *,
    size: float = 14,
    weight: ft.FontWeight | None = None,
    color_key: str = "text_secondary",
    height: float | None = 1.5,
    color: str | None = None,
) -> ft.TextStyle:
    resolved = color if color is not None else theme[color_key]
    return ft.TextStyle(
        size=size,
        weight=weight,
        color=resolved,
        height=height,
    )


def heading_style(theme: Mapping[str, Any], *, size: float = 22, weight: ft.FontWeight = ft.FontWeight.W_700) -> ft.TextStyle:
    return ft.TextStyle(size=size, weight=weight, color=theme["text"])


def display_style(
    theme: Mapping[str, Any],
    *,
    size: float = 32,
    weight: ft.FontWeight = ft.FontWeight.W_700,
) -> ft.TextStyle:
    return ft.TextStyle(size=size, weight=weight, color=theme["text"])


def caption_style(theme: Mapping[str, Any], *, size: float = 12) -> ft.TextStyle:
    return ft.TextStyle(size=size, color=theme["text_muted"])


def card_box_shadow(theme: Mapping[str, Any]) -> ft.BoxShadow:
    return ft.BoxShadow(
        spread_radius=theme["card_shadow_spread"],
        blur_radius=theme["card_shadow_blur"],
        color=theme["card_shadow_color"],
        offset=ft.Offset(0, theme["card_shadow_offset_y"]),
    )


def primary_gradient(theme: Mapping[str, Any]) -> ft.LinearGradient:
    return ft.LinearGradient(
        begin=ft.alignment.top_left,
        end=ft.alignment.bottom_right,
        colors=[theme["accent"], theme["button_gradient_end"]],
    )
