"""AuthenticatedBackground — reusable dark premium SaaS background for authenticated pages.

Uses grid overlay, ambient orbs, and glassmorphism to create a cohesive workspace feel
similar to the landing page but optimized for authenticated workspace layouts.
"""

from __future__ import annotations

import flet as ft

from ui.components.background_layers import ambient_orb, shared_auth_backdrop, subtle_grid_layer
from ui.themes.app_theme import Colors


def authenticated_workspace_background(content: ft.Control) -> ft.Control:
    """
    Wraps content with an authenticated workspace background.
    
    Args:
        content: The main content control (usually the page body)
    
    Returns:
        A Container with stacked background layers and the content on top
    """
    return ft.Container(
        expand=True,
        bgcolor=Colors.background,
        content=ft.Stack(
            expand=True,
            controls=[
                # Base backdrop
                shared_auth_backdrop(),
                # Subtle grid overlay
                subtle_grid_layer(opacity=0.04),
                # Ambient orbs for premium feel
                ambient_orb(
                    size=560,
                    color_hex=Colors.primary,
                    align_left=True,
                    align_top=True,
                    x_offset=-200,
                    y_offset=-200,
                    opacity=0.12,
                ),
                ambient_orb(
                    size=460,
                    color_hex=Colors.accent_cyan,
                    align_left=False,
                    align_top=False,
                    x_offset=-150,
                    y_offset=-180,
                    opacity=0.10,
                ),
                # Content on top
                content,
            ],
        ),
    )


def authenticated_page_background(content: ft.Control, aura_color: str = Colors.primary) -> ft.Control:
    """
    Alternative background for individual authenticated pages with custom aura color.
    Used when you want a specific accent color for a page.
    
    Args:
        content: The main content control
        aura_color: Hex color for the radial gradient aura (default: primary purple)
    
    Returns:
        A Container with animated background and content
    """
    aura = ft.Container(
        width=420, height=420,
        gradient=ft.RadialGradient(
            center=ft.alignment.center,
            radius=0.9,
            colors=[f"{aura_color}33", Colors.background],
        ),
        border_radius=999,
        right=-180, top=-160,
    )

    return ft.Container(
        expand=True,
        bgcolor=Colors.background,
        content=ft.Stack(
            expand=True,
            controls=[
                aura,
                shared_auth_backdrop(),
                subtle_grid_layer(opacity=0.04),
                content,
            ],
        ),
    )
