"""Settings page."""

from __future__ import annotations

from typing import Any, Callable, Mapping

import flet as ft

from app.config.ai_config import AIConfig
from app.models.user import User
from ui.components.glass_card import glass_card
from ui.components.page_header import page_header
from ui.themes.app_theme import Radii, Spacing
from ui.theme import caption_style, heading_style, subheading_style, text_style


def build_settings_page(
    *,
    theme: Mapping[str, Any],
    user: User,
    ai_config: AIConfig,
    is_ollama_available: bool,
    is_dark_mode_enabled: bool,
    on_theme_toggle: Callable[[ft.ControlEvent], None],
    on_logout: Callable[[ft.ControlEvent], None],
    on_clear_chat: Callable[[ft.ControlEvent], None],
) -> ft.Control:
    provider = _provider_label(user)
    profile_card = _settings_card(
        theme=theme,
        title="Account Profile",
        subtitle="Your identity and workspace account details.",
        icon=ft.icons.PERSON_ROUNDED,
        accent=theme["accent_2"],
        trailing=_badge(theme, "Active", theme["success"]),
        content=[
            _row(theme, "Name", user.full_name),
            _row(theme, "Username", user.username),
            _row(theme, "Email", user.email),
            _row(theme, "Member since", user.created_at.strftime("%b %d, %Y")),
            _row(theme, "Auth provider", _badge(theme, provider, _provider_color(theme, provider))),
        ],
    )

    appearance_card = _settings_card(
        theme=theme,
        title="Appearance",
        subtitle="Choose how StackWise AI looks on this device.",
        icon=ft.icons.DARK_MODE_ROUNDED if is_dark_mode_enabled else ft.icons.WB_SUNNY_ROUNDED,
        accent=theme["accent"],
        content=[
            ft.Container(
                padding=ft.padding.all(14),
                border_radius=Radii.md,
                bgcolor=theme["secondary_surface"],
                border=ft.border.all(1, theme["border"]),
                content=ft.Row(
                    spacing=Spacing.md,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        _icon_chip(
                            theme,
                            ft.icons.DARK_MODE_ROUNDED if is_dark_mode_enabled else ft.icons.WB_SUNNY_ROUNDED,
                            theme["accent"],
                        ),
                        ft.Column(
                            spacing=3,
                            expand=True,
                            controls=[
                                ft.Text("Theme preference", style=subheading_style(theme, size=14)),
                                ft.Text(
                                    "Choose how StackWise AI looks on this device.",
                                    style=caption_style(theme, size=12),
                                ),
                            ],
                        ),
                        ft.Switch(
                            value=is_dark_mode_enabled,
                            on_change=on_theme_toggle,
                            active_color=theme["accent_2"],
                            active_track_color=ft.colors.with_opacity(0.32, theme["accent_2"]),
                            inactive_thumb_color=theme["text_secondary"],
                            inactive_track_color=theme["surface_3"],
                            tooltip="Switch theme",
                        ),
                    ],
                ),
            ),
            ft.Row(
                controls=[
                    _badge(theme, "Current: Dark" if is_dark_mode_enabled else "Current: Light", theme["accent_2"]),
                    _badge(theme, "Synced to account", theme["success"]),
                ],
                spacing=Spacing.sm,
                wrap=True,
            ),
        ],
    )

    ai_card = _settings_card(
        theme=theme,
        title="AI Engine",
        subtitle="Local Ollama integration and response enrichment status.",
        icon=ft.icons.SMART_TOY_ROUNDED,
        accent=theme["accent_2"],
        trailing=_status_badge(theme, is_ollama_available),
        content=[
            _row(theme, "Endpoint", ai_config.base_url, mono=True),
            _row(theme, "Default model", ai_config.model, mono=True),
            _row(theme, "Streaming", _badge(theme, "Enabled" if ai_config.enable_streaming else "Disabled", theme["success"] if ai_config.enable_streaming else theme["warning"])),
            _row(
                theme,
                "Explanation enrichment",
                _badge(
                    theme,
                    "Enabled" if ai_config.enable_llm_explanations else "Disabled",
                    theme["success"] if ai_config.enable_llm_explanations else theme["warning"],
                ),
            ),
            _tip_box(
                theme,
                "Ollama setup tip",
                "Run `ollama serve` and `ollama pull llama3.2` to enable full local LLM mode.",
                ft.icons.TIPS_AND_UPDATES_ROUNDED,
            ),
        ],
    )

    data_card = _settings_card(
        theme=theme,
        title="Data Management",
        subtitle="Manage saved AI chat conversations without touching recommendations.",
        icon=ft.icons.STORAGE_ROUNDED,
        accent=theme["accent"],
        content=[
            ft.Text(
                "Clearing chat history deletes saved chatbot conversations only. Your recommendation history and generated results stay intact.",
                style=text_style(theme, size=13.5),
            ),
            _action_button(
                theme,
                "Clear chat history",
                on_click=on_clear_chat,
                icon=ft.icons.DELETE_SWEEP_ROUNDED,
                accent=theme["warning"],
            ),
        ],
    )

    session_card = _settings_card(
        theme=theme,
        title="Session / Security",
        subtitle="End this browser session when you are done working.",
        icon=ft.icons.SHIELD_ROUNDED,
        accent=theme["danger"],
        content=[
            _tip_box(
                theme,
                "Signed in as",
                f"{user.full_name} ({user.email})",
                ft.icons.VERIFIED_USER_ROUNDED,
            ),
            _action_button(
                theme,
                "Sign out",
                on_click=on_logout,
                icon=ft.icons.LOGOUT_ROUNDED,
                accent=theme["danger"],
                filled=True,
            ),
        ],
    )

    return ft.Column(
        spacing=Spacing.xl,
        controls=[
            page_header(
                eyebrow="SETTINGS",
                title="Control center for your StackWise workspace.",
                subtitle="Manage your account, theme, AI engine, data, and active session.",
                theme=theme,
            ),
            ft.ResponsiveRow(
                spacing=Spacing.md,
                run_spacing=Spacing.md,
                controls=[
                    ft.Container(col={"xs": 12, "lg": 7}, content=profile_card),
                    ft.Container(col={"xs": 12, "lg": 5}, content=appearance_card),
                    ft.Container(col={"xs": 12, "lg": 7}, content=ai_card),
                    ft.Container(col={"xs": 12, "lg": 5}, content=data_card),
                    ft.Container(col={"xs": 12}, content=session_card),
                ],
            ),
        ],
    )


def _settings_card(
    *,
    theme: Mapping[str, Any],
    title: str,
    subtitle: str,
    icon: str,
    accent: str,
    content: list[ft.Control],
    trailing: ft.Control | None = None,
) -> ft.Control:
    return glass_card(
        ft.Column(
            spacing=Spacing.lg,
            controls=[
                ft.Row(
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        _icon_chip(theme, icon, accent),
                        ft.Column(
                            spacing=2,
                            expand=True,
                            controls=[
                                ft.Text(title, style=heading_style(theme, size=17, weight=ft.FontWeight.W_700)),
                                ft.Text(subtitle, style=caption_style(theme, size=12)),
                            ],
                        ),
                        *( [trailing] if trailing is not None else [] ),
                    ],
                ),
                ft.Container(height=1, bgcolor=theme["border"]),
                ft.Column(spacing=Spacing.md, controls=content),
            ],
        ),
        theme=theme,
        padding=Spacing.xl,
        radius=Radii.xl,
        border_color_override=theme["border_strong"],
    )


def _row(
    theme: Mapping[str, Any],
    label: str,
    value: str | ft.Control,
    *,
    mono: bool = False,
) -> ft.Control:
    value_control = value if isinstance(value, ft.Control) else ft.Text(
        value,
        size=13,
        weight=ft.FontWeight.W_600,
        color=theme["text"],
        font_family="Consolas, monospace" if mono else None,
        no_wrap=False,
    )
    return ft.Container(
        padding=ft.padding.symmetric(vertical=2),
        content=ft.Row(
            spacing=Spacing.md,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Text(label, size=12.5, color=theme["text_muted"], width=160),
                ft.Container(expand=True, alignment=ft.alignment.center_right, content=value_control),
            ],
        ),
    )


def _badge(theme: Mapping[str, Any], label: str, color: str) -> ft.Control:
    return ft.Container(
        bgcolor=ft.colors.with_opacity(0.14, color),
        border=ft.border.all(1, ft.colors.with_opacity(0.36, color)),
        border_radius=Radii.pill,
        padding=ft.padding.symmetric(horizontal=10, vertical=5),
        content=ft.Text(label, size=11, weight=ft.FontWeight.W_700, color=color),
    )


def _status_badge(theme: Mapping[str, Any], available: bool) -> ft.Control:
    color = theme["success"] if available else theme["warning"]
    label = "Online" if available else "Offline"
    return ft.Container(
        bgcolor=ft.colors.with_opacity(0.14, color),
        border=ft.border.all(1, ft.colors.with_opacity(0.36, color)),
        border_radius=Radii.pill,
        padding=ft.padding.symmetric(horizontal=10, vertical=5),
        content=ft.Row(
            spacing=6,
            tight=True,
            controls=[
                ft.Container(width=6, height=6, border_radius=999, bgcolor=color),
                ft.Text(label, size=11, weight=ft.FontWeight.W_700, color=color),
            ],
        ),
    )


def _icon_chip(theme: Mapping[str, Any], icon: str, accent: str) -> ft.Control:
    return ft.Container(
        width=42,
        height=42,
        border_radius=14,
        alignment=ft.alignment.center,
        bgcolor=ft.colors.with_opacity(0.13, accent),
        border=ft.border.all(1, ft.colors.with_opacity(0.35, accent)),
        content=ft.Icon(icon, size=20, color=accent),
    )


def _tip_box(theme: Mapping[str, Any], title: str, message: str, icon: str) -> ft.Control:
    return ft.Container(
        padding=ft.padding.all(14),
        border_radius=Radii.md,
        bgcolor=theme["secondary_surface"],
        border=ft.border.all(1, theme["border"]),
        content=ft.Row(
            spacing=Spacing.md,
            vertical_alignment=ft.CrossAxisAlignment.START,
            controls=[
                _icon_chip(theme, icon, theme["accent_2"]),
                ft.Column(
                    spacing=4,
                    expand=True,
                    controls=[
                        ft.Text(title, size=13, weight=ft.FontWeight.W_700, color=theme["text"]),
                        ft.Text(message, style=text_style(theme, size=13)),
                    ],
                ),
            ],
        ),
    )


def _action_button(
    theme: Mapping[str, Any],
    text: str,
    *,
    on_click: Callable[[ft.ControlEvent], None],
    icon: str,
    accent: str,
    filled: bool = False,
) -> ft.Control:
    fg = theme["on_gradient"] if filled else accent
    bg = accent if filled else ft.colors.with_opacity(0.10, accent)
    border_color = ft.colors.with_opacity(0.44, accent)

    def on_hover(e: ft.ControlEvent) -> None:
        hovered = e.data == "true"
        e.control.scale = ft.Scale(1.01 if hovered else 1)
        e.control.bgcolor = ft.colors.with_opacity(0.16, accent) if hovered and not filled else bg
        if e.control.page:
            e.control.update()

    return ft.Container(
        height=46,
        border_radius=Radii.md,
        bgcolor=bg,
        border=ft.border.all(1, border_color),
        padding=ft.padding.symmetric(horizontal=16, vertical=12),
        alignment=ft.alignment.center,
        ink=True,
        scale=ft.Scale(1),
        animate_scale=ft.Animation(140, ft.AnimationCurve.EASE_OUT),
        on_hover=on_hover,
        on_click=on_click,
        content=ft.Row(
            tight=True,
            spacing=Spacing.sm,
            alignment=ft.MainAxisAlignment.CENTER,
            controls=[
                ft.Icon(icon, size=18, color=fg),
                ft.Text(text, size=14, weight=ft.FontWeight.W_700, color=fg),
            ],
        ),
    )


def _provider_label(user: User) -> str:
    provider = (getattr(user, "provider", None) or "").strip().lower()
    if provider == "google" or getattr(user, "google_id", None):
        return "Google"
    return "Email"


def _provider_color(theme: Mapping[str, Any], provider: str) -> str:
    if provider.lower() == "google":
        return theme["accent_2"]
    return theme["accent"]
