"""AppLayout — authenticated shell: sidebar + topbar + scrollable content.

ACTIVE AUTHENTICATED LAYOUT - Used by all authenticated pages (Dashboard, Recommendation, History, AI Chatbot, Learning Hub, Settings)

Features:
- Collapsible sidebar with smooth state management
- Professional dark SaaS design
- Responsive to sidebar width changes
- Premium glassmorphism aesthetic
"""

from __future__ import annotations

from typing import Any, Callable, Mapping, Optional

import flet as ft

from app.utils.constants import BRAND_NAME
from ui.components.background_layers import ambient_orb, themed_shared_auth_backdrop, themed_subtle_grid_layer
from ui.components.nav_rail import nav_rail
from ui.themes.app_theme import Spacing
from ui.theme import caption_style, is_dark_mode, sync_page_workspace_chrome, toggle_theme_mode


class _SidebarState:
    """Mutable state holder for sidebar collapse toggle."""
    def __init__(self):
        self.collapsed = False


def app_layout(
    *,
    page: ft.Page,
    current_route: str,
    user_name: str,
    user_email: str,
    on_navigate: Callable[[str], None],
    on_logout: Callable[[ft.ControlEvent], None],
    body: ft.Control,
    theme: Mapping[str, Any],
    topbar_actions: Optional[list[ft.Control]] = None,
) -> ft.Control:
    sync_page_workspace_chrome(page, theme)

    # Sidebar state management
    state = _SidebarState()

    # Container refs for dynamic updates
    sidebar_ref = ft.Ref[ft.Container]()
    layout_row_ref = ft.Ref[ft.Row]()
    content_area_ref = ft.Ref[ft.Container]()

    def on_toggle_collapse(_e: ft.ControlEvent) -> None:
        """Toggle sidebar collapse state and rebuild."""
        state.collapsed = not state.collapsed

        # Rebuild sidebar with new collapsed state
        new_sidebar = nav_rail(
            current_route=current_route,
            on_navigate=on_navigate,
            on_logout=on_logout,
            user_name=user_name,
            user_email=user_email,
            collapsed=state.collapsed,
            on_toggle_collapse=on_toggle_collapse,
            theme=theme,
        )

        # Update sidebar container
        if sidebar_ref.current is not None:
            sidebar_ref.current.content = new_sidebar.content
            sidebar_ref.current.width = new_sidebar.width
            sidebar_ref.current.padding = new_sidebar.padding
            sidebar_ref.current.bgcolor = new_sidebar.bgcolor
            sidebar_ref.current.border = new_sidebar.border
            if sidebar_ref.current.page:
                sidebar_ref.current.update()

    # Create initial sidebar
    sidebar = nav_rail(
        current_route=current_route,
        on_navigate=on_navigate,
        on_logout=on_logout,
        user_name=user_name,
        user_email=user_email,
        collapsed=state.collapsed,
        on_toggle_collapse=on_toggle_collapse,
        theme=theme,
    )

    # Sidebar container with ref for dynamic updates
    sidebar_container = ft.Container(
        ref=sidebar_ref,
        width=sidebar.width,
        bgcolor=sidebar.bgcolor,
        border=sidebar.border,
        padding=sidebar.padding,
        content=sidebar.content,
    )

    def on_theme_toggle(_e: ft.ControlEvent) -> None:
        toggle_theme_mode(_e.page)
        r = getattr(_e.page, "_stackwise_router", None)
        if r is not None:
            r.reload_current_view()

    dark = is_dark_mode(page)
    theme_toggle = ft.IconButton(
        icon="wb_sunny_rounded" if dark else "dark_mode_rounded",
        icon_size=20,
        icon_color=theme["text_secondary"],
        tooltip="Switch to Light Mode" if dark else "Switch to Dark Mode",
        on_click=on_theme_toggle,
    )

    merged_topbar_actions = [theme_toggle, *(topbar_actions or [])]

    topbar = ft.Container(
        height=64,
        bgcolor=ft.colors.with_opacity(theme["topbar_bg_alpha"], theme["topbar_bg_base"]),
        border=ft.border.only(bottom=ft.BorderSide(1, theme["border"])),
        padding=ft.padding.symmetric(horizontal=Spacing.xxl, vertical=Spacing.md),
        content=ft.Row(
            controls=[
                ft.Row(
                    spacing=Spacing.sm,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Container(
                            width=8, height=8, border_radius=999,
                            gradient=ft.LinearGradient(
                                begin=ft.alignment.top_left, end=ft.alignment.bottom_right,
                                colors=[theme["accent"], theme["accent_2"]],
                            ),
                        ),
                        ft.Text(BRAND_NAME, size=13, weight=ft.FontWeight.W_700, color=theme["text"]),
                        ft.Container(width=Spacing.md),
                        ft.Text(
                            _route_breadcrumb(current_route),
                            style=caption_style(theme, size=12),
                        ),
                    ],
                ),
                ft.Container(expand=1),
                ft.Row(
                    spacing=Spacing.md,
                    controls=merged_topbar_actions,
                ),
            ],
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
    )

    content_area = ft.Container(
        ref=content_area_ref,
        expand=True,
        padding=ft.padding.only(left=Spacing.xxxl, right=Spacing.xxxl, top=Spacing.xxl, bottom=Spacing.xxl),
        # Transparent background to show workspace background through
        bgcolor="transparent",
        content=ft.Column(
            scroll=ft.ScrollMode.AUTO,
            controls=[body],
            expand=True,
        ),
    )

    main_column = ft.Column(
        controls=[topbar, content_area],
        spacing=0,
        expand=True,
    )

    layout_row = ft.Row(
        ref=layout_row_ref,
        controls=[sidebar_container, main_column],
        spacing=0, expand=True,
        vertical_alignment=ft.CrossAxisAlignment.START,
    )

    # SHARED AUTHENTICATED WORKSPACE BACKGROUND
    background = ft.Container(
        expand=True,
        bgcolor=theme["page_bg"],
        content=ft.Stack(
            expand=True,
            controls=[
                themed_shared_auth_backdrop(theme),
                themed_subtle_grid_layer(theme),
                ambient_orb(
                    size=560,
                    color_hex=theme["accent"],
                    align_left=True,
                    align_top=True,
                    x_offset=-200,
                    y_offset=-200,
                    opacity=theme["orb_primary_opacity"],
                    fade_to=theme["orb_fade"],
                ),
                ambient_orb(
                    size=460,
                    color_hex=theme["accent_2"],
                    align_left=False,
                    align_top=False,
                    x_offset=-150,
                    y_offset=-180,
                    opacity=theme["orb_cyan_opacity"],
                    fade_to=theme["orb_fade"],
                ),
                layout_row,
            ],
        ),
    )

    return background


def _route_breadcrumb(route: str) -> str:
    crumb = route.strip("/").replace("-", " ").title() or "Dashboard"
    return f"  /  {crumb}"
