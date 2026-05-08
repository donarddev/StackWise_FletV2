"""Chatbot page — full-height chat panel."""

from __future__ import annotations

from typing import Callable

import flet as ft

from app.models.chatbot_log import ChatbotLog
from ui.components.empty_state import empty_state
from ui.components.glass_card import glass_card
from ui.components.input_field import input_field
from ui.components.page_header import page_header
from ui.components.primary_button import primary_button, secondary_button
from ui.themes.app_theme import Colors, Radii, Spacing, Typography
from ui.widgets.chat_bubble import chat_bubble


SUGGESTED_PROMPTS = [
    "What language should I use for an AI side-project I want to ship in 4 weeks?",
    "Explain the difference between Agile, Kanban, and Waterfall.",
    "When should I pick FastAPI over Django?",
    "Help me decide between Flutter and React Native.",
]


def build_chatbot_page(
    *,
    user_name: str,
    history: list[ChatbotLog],
    is_ollama_available: bool,
    input_field_ref: ft.Ref[ft.TextField],
    messages_column_ref: ft.Ref[ft.Column],
    on_send: Callable[[str], None],
    on_clear: Callable[[ft.ControlEvent], None],
) -> ft.Control:
    chat_input = input_field(
        "Ask anything — languages, frameworks, SDLC, your last recommendation…",
        icon=ft.icons.CHAT_BUBBLE_OUTLINE,
        on_submit=lambda e: on_send(e.control.value or ""),
    )
    chat_input.ref = input_field_ref

    send_btn = primary_button(
        "Send",
        on_click=lambda _e: on_send(chat_input.value or ""),
        icon=ft.icons.SEND_ROUNDED,
        height=48,
    )

    composer = ft.Container(
        bgcolor=Colors.surface,
        border=ft.border.all(1, Colors.border),
        border_radius=Radii.lg,
        padding=ft.padding.all(Spacing.md),
        content=ft.Row(
            spacing=Spacing.md,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Container(content=chat_input, expand=True),
                send_btn,
            ],
        ),
    )

    initial_controls: list[ft.Control] = []
    if not history:
        initial_controls.append(_welcome_block(user_name, is_ollama_available, on_send))
    else:
        for log in history:
            initial_controls.append(
                chat_bubble(role=log.role, content=log.content, author_name=user_name)
            )

    messages = ft.Column(
        controls=initial_controls,
        spacing=Spacing.lg,
        scroll=ft.ScrollMode.ADAPTIVE,
        ref=messages_column_ref,
        expand=True,
    )

    chat_panel = ft.Container(
        expand=True,
        bgcolor=Colors.surface_2,
        border=ft.border.all(1, Colors.border),
        border_radius=Radii.lg,
        padding=ft.padding.all(Spacing.lg),
        content=ft.Column(
            controls=[messages],
            expand=True,
        ),
    )

    return ft.Column(
        spacing=Spacing.xl,
        controls=[
            page_header(
                eyebrow="AI CHATBOT",
                title="Talk to StackWise.",
                subtitle=(
                    "Ollama-powered. Falls back gracefully when offline."
                    if is_ollama_available
                    else "Currently in offline fallback mode (Ollama not detected)."
                ),
                trailing=secondary_button(
                    "Clear conversation",
                    on_click=on_clear,
                    icon=ft.icons.CLEAR_ALL,
                ),
            ),
            ft.Container(content=chat_panel, height=520),
            composer,
        ],
    )


def _welcome_block(
    user_name: str, available: bool, on_send: Callable[[str], None]
) -> ft.Control:
    pills = []
    for prompt in SUGGESTED_PROMPTS:
        pills.append(
            ft.Container(
                bgcolor=Colors.surface,
                border=ft.border.all(1, Colors.border),
                border_radius=Radii.pill,
                padding=ft.padding.symmetric(horizontal=14, vertical=8),
                ink=True,
                on_click=lambda _e, p=prompt: on_send(p),
                content=ft.Text(prompt, size=12.5, color=Colors.text_secondary),
            )
        )
    pills_row = ft.Row(spacing=Spacing.sm, run_spacing=Spacing.sm, wrap=True, controls=pills)

    status = (
        "Ollama is running locally — full LLM mode."
        if available
        else "Running in offline mode — answers come from a curated knowledge base."
    )

    body = ft.Column(
        spacing=Spacing.md,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        controls=[
            ft.Container(
                width=72, height=72, border_radius=20,
                gradient=ft.LinearGradient(
                    begin=ft.alignment.top_left, end=ft.alignment.bottom_right,
                    colors=[Colors.primary, Colors.accent_cyan],
                ),
                alignment=ft.alignment.center,
                content=ft.Icon(ft.icons.AUTO_AWESOME, size=32, color=Colors.text_primary),
            ),
            ft.Text(
                f"Hi {user_name.split()[0]} — I'm StackWise.",
                style=Typography.subheading(size=18), text_align=ft.TextAlign.CENTER,
            ),
            ft.Text(status, style=Typography.body(), text_align=ft.TextAlign.CENTER),
            ft.Container(height=Spacing.md),
            ft.Text("Try one of these:", style=Typography.caption(),
                    text_align=ft.TextAlign.CENTER),
            pills_row,
        ],
    )
    return glass_card(body)
