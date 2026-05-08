"""Settings page."""

from __future__ import annotations

from typing import Callable

import flet as ft

from app.config.ai_config import AIConfig
from app.models.user import User
from ui.components.glass_card import glass_card
from ui.components.page_header import page_header
from ui.components.primary_button import secondary_button
from ui.themes.app_theme import Colors, Radii, Spacing, Typography


def build_settings_page(
    *,
    user: User,
    ai_config: AIConfig,
    is_ollama_available: bool,
    on_logout: Callable[[ft.ControlEvent], None],
    on_clear_chat: Callable[[ft.ControlEvent], None],
) -> ft.Control:
    profile_card = glass_card(
        ft.Column(
            spacing=Spacing.md,
            controls=[
                ft.Text("Profile", style=Typography.subheading(size=15)),
                _row("Name", user.full_name),
                _row("Username", user.username),
                _row("Email", user.email),
                _row("Member since", user.created_at.strftime("%b %d, %Y")),
                ft.Container(height=Spacing.sm),
                secondary_button("Sign out", on_click=on_logout, icon=ft.icons.LOGOUT),
            ],
        )
    )

    ai_card = glass_card(
        ft.Column(
            spacing=Spacing.md,
            controls=[
                ft.Row(
                    controls=[
                        ft.Text("AI engine", style=Typography.subheading(size=15)),
                        ft.Container(expand=1),
                        _status_pill(is_ollama_available),
                    ],
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                _row("Endpoint", ai_config.base_url),
                _row("Default model", ai_config.model),
                _row("Streaming", "Enabled" if ai_config.enable_streaming else "Disabled"),
                _row(
                    "Explanation enrichment",
                    "On" if ai_config.enable_llm_explanations else "Off",
                ),
                ft.Container(height=Spacing.sm),
                ft.Text(
                    "Tip: install Ollama and run `ollama pull llama3.2` to enable full LLM mode.",
                    style=Typography.caption(),
                ),
            ],
        )
    )

    chat_card = glass_card(
        ft.Column(
            spacing=Spacing.md,
            controls=[
                ft.Text("Chat data", style=Typography.subheading(size=15)),
                ft.Text(
                    "Your conversation history is stored in the `chatbot_logs` table "
                    "of your StackWise AI MySQL database. Clearing it doesn't affect "
                    "your recommendations.",
                    style=Typography.body(),
                ),
                secondary_button(
                    "Clear chat history",
                    on_click=on_clear_chat,
                    icon=ft.icons.CLEAR_ALL,
                ),
            ],
        )
    )

    return ft.Column(
        spacing=Spacing.xl,
        controls=[
            page_header(
                eyebrow="SETTINGS",
                title="Account & engine settings.",
                subtitle="Configure how StackWise integrates into your workflow.",
            ),
            ft.ResponsiveRow(
                spacing=Spacing.md, run_spacing=Spacing.md,
                controls=[
                    ft.Container(col={"xs": 12, "md": 6}, content=profile_card),
                    ft.Container(col={"xs": 12, "md": 6}, content=ai_card),
                    ft.Container(col={"xs": 12}, content=chat_card),
                ],
            ),
        ],
    )


def _row(label: str, value: str) -> ft.Control:
    return ft.Row(
        controls=[
            ft.Text(label, size=12.5, color=Colors.text_muted, width=140),
            ft.Text(value, size=13, weight=ft.FontWeight.W_600, color=Colors.text_primary),
        ],
        spacing=Spacing.md,
    )


def _status_pill(available: bool) -> ft.Control:
    color = Colors.success if available else Colors.warning
    label = "Online" if available else "Offline (fallback)"
    return ft.Container(
        bgcolor=ft.colors.with_opacity(0.16, color),
        border=ft.border.all(1, ft.colors.with_opacity(0.4, color)),
        border_radius=Radii.pill,
        padding=ft.padding.symmetric(horizontal=10, vertical=4),
        content=ft.Row(
            spacing=6, tight=True,
            controls=[
                ft.Container(width=6, height=6, border_radius=999, bgcolor=color),
                ft.Text(label, size=11, weight=ft.FontWeight.W_700, color=color),
            ],
        ),
    )
