"""NavRail — sidebar navigation used by AppLayout.

ACTIVE AUTHENTICATED SIDEBAR — Collapsible professional dark SaaS sidebar
inspired by Vercel, Linear, and Notion.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Mapping, Optional

import flet as ft

from app.utils.constants import BRAND_NAME, Routes
from ui.dialogs.confirm_dialog import show_sign_out_dialog
from ui.themes.app_theme import Radii, Spacing
from ui.theme import caption_style


@dataclass
class NavItem:
    route: str
    label: str
    icon: str
    icon_selected: str


NAV_ITEMS: list[NavItem] = [
    NavItem(Routes.DASHBOARD, "Dashboard", "space_dashboard_outlined", "space_dashboard"),
    NavItem(Routes.RECOMMENDATION, "Recommendation", "auto_awesome_outlined", "auto_awesome"),
    NavItem(Routes.HISTORY, "History", "history_outlined", "history"),
    NavItem(Routes.CHATBOT, "AI Chatbot", "chat_bubble_outlined", "chat_bubble"),
    NavItem(Routes.LEARNING, "Learning Hub", "menu_book_outlined", "menu_book"),
    NavItem(Routes.SETTINGS, "Settings", "settings_outlined", "settings"),
]


def nav_rail(
    *,
    current_route: str,
    on_navigate: Callable[[str], None],
    on_logout: Callable[[ft.ControlEvent], None],
    user_name: str,
    user_email: str,
    collapsed: bool = False,
    on_toggle_collapse: Optional[Callable[[ft.ControlEvent], None]] = None,
    theme: Mapping[str, Any],
) -> ft.Container:
    def on_confirm_logout(e: ft.ControlEvent) -> None:
        if e.page is None:
            return
        show_sign_out_dialog(
            e.page,
            theme=theme,
            on_confirm=lambda: on_logout(e),
        )

    # Build nav items with collapsed state
    nav_items_controls = [
        _nav_item(
            it,
            theme=theme,
            selected=(it.route == current_route),
            on_navigate=on_navigate,
            collapsed=collapsed,
        )
        for it in NAV_ITEMS
    ]

    # Brand section — shows full logo + text when expanded, compact when collapsed
    if collapsed:
        brand = ft.Container(
            alignment=ft.alignment.center,
            height=40,
            content=__import__("ui.components.brand_logo", fromlist=["brand_icon"]).brand_icon(
                size=32, radius=8
            ),
        )
    else:
        brand = ft.Row(
            controls=[
                __import__("ui.components.brand_logo", fromlist=["brand_icon"]).brand_icon(size=38, radius=10),
                ft.Column(
                    controls=[
                        ft.Text(BRAND_NAME, size=15, weight=ft.FontWeight.W_700, color=theme["text"]),
                        ft.Text("AI workspace", size=11, color=theme["text_muted"]),
                    ],
                    spacing=0, tight=True,
                ),
            ],
            spacing=Spacing.md,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )

    # Collapse/expand button
    collapse_button = ft.IconButton(
        icon="unfold_less_rounded" if not collapsed else "unfold_more_rounded",
        icon_size=18,
        icon_color=theme["text_secondary"],
        tooltip="Toggle sidebar" if not collapsed else "Expand sidebar",
        on_click=on_toggle_collapse,
    )

    # Navigation header
    nav_header = (
        ft.Text("NAVIGATION", style=caption_style(theme, size=11))
        if not collapsed else ft.Container()
    )

    # Navigation items column
    navigation_section = ft.Column(
        controls=nav_items_controls,
        spacing=Spacing.sm,
    )

    # User profile section — changes based on collapsed state
    if collapsed:
        user_block = ft.Container(
            padding=Spacing.sm,
            alignment=ft.alignment.center,
            content=ft.Column(
                controls=[
                    ft.Container(
                        content=ft.Text(
                            (user_name[:1] or "U").upper(),
                            size=13, weight=ft.FontWeight.W_700, color=theme["text"],
                            text_align=ft.TextAlign.CENTER,
                        ),
                        width=36, height=36,
                        bgcolor=theme["surface_3"],
                        border_radius=10,
                        border=ft.border.all(1, theme["border"]),
                        alignment=ft.alignment.center,
                    ),
                    ft.IconButton(
                        icon="logout_rounded",
                        icon_size=16,
                        icon_color=theme["text_secondary"],
                        tooltip="Sign out",
                        on_click=on_confirm_logout,
                    ),
                ],
                spacing=Spacing.xs,
                alignment=ft.MainAxisAlignment.CENTER,
            ),
        )
    else:
        user_block = ft.Container(
            padding=Spacing.md,
            bgcolor=theme["surface_2"],
            border=ft.border.all(1, theme["border"]),
            border_radius=Radii.md,
            content=ft.Row(
                controls=[
                    ft.Container(
                        content=ft.Text(
                            (user_name[:1] or "U").upper(),
                            size=14, weight=ft.FontWeight.W_700, color=theme["text"],
                            text_align=ft.TextAlign.CENTER,
                        ),
                        width=34, height=34,
                        bgcolor=theme["surface_3"],
                        border_radius=10,
                        alignment=ft.alignment.center,
                    ),
                    ft.Column(
                        controls=[
                            ft.Text(user_name, size=13, weight=ft.FontWeight.W_600, color=theme["text"]),
                            ft.Text(user_email, size=11, color=theme["text_muted"]),
                        ],
                        spacing=0, tight=True, expand=True,
                    ),
                    ft.IconButton(
                        icon="logout_rounded",
                        icon_size=18,
                        icon_color=theme["text_secondary"],
                        tooltip="Sign out",
                        on_click=on_confirm_logout,
                    ),
                ],
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=Spacing.md,
            ),
        )

    # Brand header with collapse button (expanded mode only)
    if collapsed:
        brand_section = ft.Container(
            height=50,
            content=ft.Row(
                controls=[brand],
                alignment=ft.MainAxisAlignment.CENTER,
            ),
        )
    else:
        brand_section = ft.Row(
            controls=[
                ft.Container(expand=True, content=brand),
                collapse_button,
            ],
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=Spacing.sm,
        )

    # Sidebar width based on collapsed state
    sidebar_width = 80 if collapsed else 280

    # Main sidebar content
    sidebar_content = ft.Column(
        controls=[
            brand_section,
            ft.Container(height=Spacing.lg if not collapsed else Spacing.md),
            nav_header,
            ft.Container(height=Spacing.sm if not collapsed else 0),
            navigation_section,
            ft.Container(expand=1),
            user_block,
            ft.Container(height=Spacing.sm if not collapsed else 0),
            collapse_button if collapsed else ft.Container(),
        ],
        spacing=0,
        expand=True,
    )

    return ft.Container(
        width=sidebar_width,
        bgcolor=theme["sidebar_bg"],
        border=ft.border.only(right=ft.BorderSide(1, theme["border"])),
        padding=ft.padding.symmetric(
            horizontal=Spacing.md if collapsed else 18,
            vertical=Spacing.md if collapsed else 22
        ),
        content=sidebar_content,
    )


def _nav_item(
    item: NavItem,
    *,
    theme: Mapping[str, Any],
    selected: bool,
    on_navigate: Callable[[str], None],
    collapsed: bool = False,
) -> ft.Control:
    accent = theme["accent"]
    bgcolor = ft.colors.with_opacity(theme["nav_selected_alpha"], accent) if selected else "transparent"
    text_color = theme["text"] if selected else theme["text_secondary"]
    icon_color = theme["accent_glow"] if selected else theme["text_secondary"]

    # Accent bar shown only for selected item (expanded mode only)
    accent_bar = ft.Container(
        width=4, height=18,
        bgcolor=accent,
        border_radius=2
    ) if selected and not collapsed else None

    # Create ref for hover state management
    item_container = ft.Ref[ft.Container]()

    def on_hover(e: ft.HoverEvent) -> None:
        if item_container.current is None:
            return
        if e.data == "true":  # mouse over
            item_container.current.bgcolor = ft.colors.with_opacity(
                theme["nav_hover_selected_alpha"] if selected else theme["nav_hover_alpha"],
                accent,
            )
        else:  # mouse out
            item_container.current.bgcolor = ft.colors.with_opacity(
                theme["nav_selected_alpha"] if selected else 0, accent
            )
        if item_container.current.page:
            item_container.current.update()

    # Collapsed mode: center icons only
    if collapsed:
        return ft.Container(
            ref=item_container,
            on_click=lambda _e: on_navigate(item.route),
            on_hover=on_hover,
            ink=True,
            bgcolor=bgcolor,
            border_radius=Radii.md,
            padding=Spacing.md,
            width=48, height=48,
            alignment=ft.alignment.center,
            tooltip=item.label,
            content=ft.Icon(
                item.icon_selected if selected else item.icon,
                size=20,
                color=icon_color,
            ),
        )
    else:
        # Expanded mode: show icon + label with accent bar
        return ft.Container(
            ref=item_container,
            on_click=lambda _e: on_navigate(item.route),
            on_hover=on_hover,
            ink=True,
            bgcolor=bgcolor,
            border_radius=Radii.md,
            padding=ft.padding.symmetric(horizontal=12, vertical=10),
            content=ft.Row(
                controls=[
                    ft.Icon(
                        item.icon_selected if selected else item.icon,
                        size=18,
                        color=icon_color,
                    ),
                    ft.Text(
                        item.label,
                        size=13.5,
                        weight=ft.FontWeight.W_600,
                        color=text_color,
                    ),
                    ft.Container(expand=1),
                    *(([accent_bar]) if accent_bar else []),
                ],
                spacing=Spacing.md,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
        )
