"""Shared dashboard glass colors — stronger contrast in dark workspace, theme-safe in light."""

from __future__ import annotations

from typing import Any, Mapping


def dashboard_glass_tokens(theme: Mapping[str, Any]) -> dict[str, str]:
    """Return hex/RGB strings for dashboard-only glass surfaces."""
    if str(theme.get("page_bg", "")).lower() == "#020617":
        return {
            "card_bg": "#132033",
            "card_border": "#2A3B55",
            "card_hover": "#152a42",
            "teal": "#22D3EE",
            "panel_bg": "#0D1B2A",
            "panel_border": "#1a2d45",
            "header_bg": "#111C2E",
            "header_border": "#24344D",
            "divider": "#24344D",
        }
    return {
        "card_bg": str(theme["card_bg"]),
        "card_border": str(theme["border_strong"]),
        "card_hover": str(theme["surface_3"]),
        "teal": str(theme["accent_2"]),
        "panel_bg": str(theme["surface_2"]),
        "panel_border": str(theme["border"]),
        "header_bg": str(theme["surface_3"]),
        "header_border": str(theme["border"]),
        "divider": str(theme["border"]),
    }
