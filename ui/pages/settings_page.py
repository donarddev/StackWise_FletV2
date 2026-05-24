"""Settings page — professional control center (dark glass)."""

from __future__ import annotations

from typing import Any, Callable, Mapping, Optional

import flet as ft

from app.config.ai_config import AIConfig
from app.models.user import User
from ui.themes.app_theme import Radii, Spacing

# Control center palette (dark workspace)
_S_PAGE_BG = "#07111F"
_S_CARD_BG = "#101B2E"
_S_CARD_SOFT = "#13243A"
_S_NESTED = "#0D1728"
_S_BORDER = "#223A56"
_S_CYAN = "#22D3EE"
_S_PURPLE = "#8B5CF6"
_S_SUCCESS = "#34D399"
_S_WARNING = "#FBBF24"
_S_DANGER = "#F87171"
_S_TEXT = "#F8FAFC"
_S_MUTED = "#94A3B8"
_S_SUBTLE = "#64748B"

_CARD_RADIUS = 20
_CARD_PAD = 22
_ROW_DIVIDER = ft.BorderSide(1, ft.colors.with_opacity(0.35, _S_BORDER))


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
    """Main Settings page body."""
    return ft.Container(
        bgcolor=_S_PAGE_BG,
        padding=ft.padding.only(bottom=Spacing.lg),
        content=ft.Column(
            spacing=Spacing.xl,
            controls=[
                build_settings_header(),
                ft.ResponsiveRow(
                    spacing=Spacing.md,
                    run_spacing=Spacing.md,
                    vertical_alignment=ft.CrossAxisAlignment.START,
                    controls=[
                        ft.Container(
                            col={"xs": 12, "lg": 6},
                            content=build_account_profile_card(user, theme),
                        ),
                        ft.Container(
                            col={"xs": 12, "lg": 6},
                            content=build_appearance_card(
                                theme,
                                is_dark_mode_enabled=is_dark_mode_enabled,
                                on_theme_toggle=on_theme_toggle,
                            ),
                        ),
                        ft.Container(
                            col={"xs": 12, "lg": 6},
                            content=build_ai_engine_card(
                                theme,
                                ai_config=ai_config,
                                is_ollama_available=is_ollama_available,
                            ),
                        ),
                        ft.Container(
                            col={"xs": 12, "lg": 6},
                            content=build_data_management_card(
                                theme,
                                on_clear_chat=on_clear_chat,
                            ),
                        ),
                        ft.Container(
                            col={"xs": 12},
                            content=build_session_security_card(
                                theme,
                                user=user,
                                on_logout=on_logout,
                            ),
                        ),
                    ],
                ),
            ],
        ),
    )


def build_settings_header() -> ft.Control:
    return ft.Column(
        spacing=Spacing.sm,
        controls=[
            ft.Container(
                content=ft.Text(
                    "SETTINGS",
                    size=11,
                    weight=ft.FontWeight.W_700,
                    color=_S_CYAN,
                ),
                bgcolor=ft.colors.with_opacity(0.12, _S_CYAN),
                border=ft.border.all(1, ft.colors.with_opacity(0.35, _S_CYAN)),
                border_radius=Radii.pill,
                padding=ft.padding.symmetric(horizontal=10, vertical=4),
            ),
            ft.Text(
                "Control center for your StackWise workspace.",
                size=28,
                weight=ft.FontWeight.W_700,
                color=_S_TEXT,
            ),
            ft.Text(
                "Manage your account, theme, AI engine, data, and active session.",
                size=14,
                color=_S_MUTED,
            ),
        ],
    )


def build_settings_card(
    *,
    title: str,
    subtitle: str,
    icon: str,
    accent: str,
    content: list[ft.Control],
    status_badge: Optional[ft.Control] = None,
) -> ft.Control:
    header_controls: list[ft.Control] = [
        _icon_badge(icon, accent),
        ft.Column(
            spacing=3,
            expand=True,
            controls=[
                ft.Text(title, size=17, weight=ft.FontWeight.W_700, color=_S_TEXT),
                ft.Text(subtitle, size=12, color=_S_MUTED),
            ],
        ),
    ]
    if status_badge is not None:
        header_controls.append(status_badge)

    return ft.Container(
        bgcolor=_S_CARD_BG,
        border=ft.border.all(1, _S_BORDER),
        border_radius=_CARD_RADIUS,
        padding=_CARD_PAD,
        shadow=ft.BoxShadow(
            spread_radius=0,
            blur_radius=18,
            color="#00000035",
            offset=ft.Offset(0, 6),
        ),
        content=ft.Column(
            spacing=Spacing.lg,
            controls=[
                ft.Row(
                    vertical_alignment=ft.CrossAxisAlignment.START,
                    spacing=Spacing.md,
                    controls=header_controls,
                ),
                ft.Container(height=1, bgcolor=ft.colors.with_opacity(0.5, _S_BORDER)),
                ft.Column(spacing=Spacing.sm, controls=content),
            ],
        ),
    )


def build_setting_row(
    label: str,
    value: str | ft.Control,
    *,
    mono: bool = False,
    last: bool = False,
) -> ft.Control:
    if isinstance(value, ft.Control):
        value_control = value
    else:
        value_control = ft.Text(
            value or "—",
            size=13,
            weight=ft.FontWeight.W_600,
            color=_S_TEXT,
            font_family="Consolas, monospace" if mono else None,
            selectable=True,
        )

    return ft.Container(
        padding=ft.padding.symmetric(vertical=10),
        border=None if last else ft.border.only(bottom=_ROW_DIVIDER),
        content=ft.Row(
            spacing=Spacing.md,
            vertical_alignment=ft.CrossAxisAlignment.START,
            controls=[
                ft.Text(label, size=12, color=_S_MUTED, width=148),
                ft.Container(expand=True, content=value_control),
            ],
        ),
    )


def build_status_badge(text: str, *, status: str = "info") -> ft.Control:
    colors = {
        "info": _S_CYAN,
        "success": _S_SUCCESS,
        "warning": _S_WARNING,
        "danger": _S_DANGER,
        "purple": _S_PURPLE,
    }
    color = colors.get(status, _S_CYAN)
    dot = ft.Container(width=6, height=6, border_radius=999, bgcolor=color)
    return ft.Container(
        bgcolor=ft.colors.with_opacity(0.12, color),
        border=ft.border.all(1, ft.colors.with_opacity(0.38, color)),
        border_radius=Radii.pill,
        padding=ft.padding.symmetric(horizontal=10, vertical=5),
        content=ft.Row(
            spacing=6,
            tight=True,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                dot,
                ft.Text(text, size=11, weight=ft.FontWeight.W_700, color=color),
            ],
        ),
    )


def build_account_profile_card(user: User, theme: Mapping[str, Any]) -> ft.Control:
    provider = _provider_label(user)
    provider_color = _S_CYAN if provider.lower() == "google" else _S_PURPLE
    initials = _user_initials(user)

    avatar = ft.Container(
        width=48,
        height=48,
        border_radius=14,
        alignment=ft.alignment.center,
        bgcolor=ft.colors.with_opacity(0.14, _S_CYAN),
        border=ft.border.all(1, ft.colors.with_opacity(0.4, _S_CYAN)),
        content=ft.Text(initials, size=16, weight=ft.FontWeight.W_700, color=_S_CYAN),
    )

    header = ft.Row(
        spacing=Spacing.md,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
        controls=[
            avatar,
            ft.Column(
                spacing=2,
                expand=True,
                controls=[
                    ft.Text("Account Profile", size=17, weight=ft.FontWeight.W_700, color=_S_TEXT),
                    ft.Text(
                        "Your identity and workspace account details.",
                        size=12,
                        color=_S_MUTED,
                    ),
                ],
            ),
            build_status_badge("Active", status="success"),
        ],
    )

    body = ft.Column(
        spacing=0,
        controls=[
            build_setting_row("Name", user.full_name),
            build_setting_row("Username", user.username),
            build_setting_row("Email", user.email),
            build_setting_row("Member since", user.created_at.strftime("%b %d, %Y")),
            build_setting_row(
                "Auth provider",
                _pill_badge(provider, provider_color),
                last=True,
            ),
        ],
    )

    return ft.Container(
        bgcolor=_S_CARD_BG,
        border=ft.border.all(1, _S_BORDER),
        border_radius=_CARD_RADIUS,
        padding=_CARD_PAD,
        shadow=ft.BoxShadow(
            spread_radius=0,
            blur_radius=18,
            color="#00000035",
            offset=ft.Offset(0, 6),
        ),
        content=ft.Column(spacing=Spacing.lg, controls=[header, ft.Container(height=1, bgcolor=ft.colors.with_opacity(0.5, _S_BORDER)), body]),
    )


def build_appearance_card(
    theme: Mapping[str, Any],
    *,
    is_dark_mode_enabled: bool,
    on_theme_toggle: Callable[[ft.ControlEvent], None],
) -> ft.Control:
    theme_icon = ft.icons.DARK_MODE_ROUNDED if is_dark_mode_enabled else ft.icons.WB_SUNNY_ROUNDED

    toggle_block = ft.Container(
        padding=ft.padding.all(14),
        border_radius=14,
        bgcolor=_S_NESTED,
        border=ft.border.all(1, ft.colors.with_opacity(0.45, _S_BORDER)),
        content=ft.Row(
            spacing=Spacing.md,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                _icon_badge(theme_icon, _S_PURPLE),
                ft.Column(
                    spacing=3,
                    expand=True,
                    controls=[
                        ft.Text("Theme preference", size=14, weight=ft.FontWeight.W_600, color=_S_TEXT),
                        ft.Text(
                            "Switch between light and dark workspace themes.",
                            size=12,
                            color=_S_MUTED,
                        ),
                    ],
                ),
                ft.Switch(
                    value=is_dark_mode_enabled,
                    on_change=on_theme_toggle,
                    active_color=_S_PURPLE,
                    active_track_color=ft.colors.with_opacity(0.32, _S_PURPLE),
                    inactive_thumb_color=_S_MUTED,
                    inactive_track_color=_S_NESTED,
                    tooltip="Switch theme",
                ),
            ],
        ),
    )

    badges = ft.Row(
        spacing=Spacing.sm,
        wrap=True,
        controls=[
            build_status_badge(
                "Current: Dark" if is_dark_mode_enabled else "Current: Light",
                status="purple",
            ),
            build_status_badge("Synced to account", status="success"),
        ],
    )

    return build_settings_card(
        title="Appearance",
        subtitle="Choose how StackWise AI looks on this device.",
        icon=theme_icon,
        accent=_S_PURPLE,
        content=[toggle_block, badges],
    )


def build_ai_engine_card(
    theme: Mapping[str, Any],
    *,
    ai_config: AIConfig,
    is_ollama_available: bool,
) -> ft.Control:
    status = build_status_badge(
        "Online" if is_ollama_available else "Offline",
        status="success" if is_ollama_available else "warning",
    )

    rows = [
        build_setting_row("Endpoint", ai_config.base_url, mono=True),
        build_setting_row("Default model", ai_config.model, mono=True),
        build_setting_row(
            "Streaming",
            _pill_badge(
                "Enabled" if ai_config.enable_streaming else "Disabled",
                _S_SUCCESS if ai_config.enable_streaming else _S_WARNING,
            ),
        ),
        build_setting_row(
            "Explanation enrichment",
            _pill_badge(
                "Enabled" if ai_config.enable_llm_explanations else "Disabled",
                _S_SUCCESS if ai_config.enable_llm_explanations else _S_WARNING,
            ),
            last=True,
        ),
    ]

    tip = _info_callout(
        "Ollama setup tip",
        "Run `ollama serve` and `ollama pull llama3.2` to enable full local LLM mode.",
        ft.icons.TIPS_AND_UPDATES_ROUNDED,
    )

    return build_settings_card(
        title="AI Engine",
        subtitle="Local Ollama integration and response enrichment status.",
        icon=ft.icons.SMART_TOY_ROUNDED,
        accent=_S_CYAN,
        status_badge=status,
        content=[*rows, tip],
    )


def build_data_management_card(
    theme: Mapping[str, Any],
    *,
    on_clear_chat: Callable[[ft.ControlEvent], None],
) -> ft.Control:
    note = ft.Container(
        padding=ft.padding.all(14),
        border_radius=14,
        bgcolor=_S_NESTED,
        border=ft.border.all(1, ft.colors.with_opacity(0.4, _S_WARNING)),
        content=ft.Row(
            spacing=Spacing.md,
            vertical_alignment=ft.CrossAxisAlignment.START,
            controls=[
                ft.Icon(ft.icons.INFO_OUTLINE, size=18, color=_S_WARNING),
                ft.Column(
                    spacing=4,
                    expand=True,
                    controls=[
                        ft.Text(
                            "Chat history only",
                            size=13,
                            weight=ft.FontWeight.W_600,
                            color=_S_TEXT,
                        ),
                        ft.Text(
                            "Clearing chat history deletes saved chatbot conversations only. "
                            "Your recommendation history and generated results stay intact.",
                            size=12,
                            color=_S_MUTED,
                        ),
                    ],
                ),
            ],
        ),
    )

    clear_btn = _settings_button(
        "Clear chat history",
        on_click=on_clear_chat,
        icon=ft.icons.DELETE_SWEEP_ROUNDED,
        kind="warning",
    )

    return build_settings_card(
        title="Data Management",
        subtitle="Manage saved AI chat without affecting recommendations.",
        icon=ft.icons.STORAGE_ROUNDED,
        accent=_S_CYAN,
        content=[
            note,
            ft.Row(
                alignment=ft.MainAxisAlignment.START,
                controls=[clear_btn],
            ),
        ],
    )


def build_session_security_card(
    theme: Mapping[str, Any],
    *,
    user: User,
    on_logout: Callable[[ft.ControlEvent], None],
) -> ft.Control:
    session_panel = ft.Container(
        expand=True,
        padding=ft.padding.all(14),
        border_radius=14,
        bgcolor=_S_NESTED,
        border=ft.border.all(1, ft.colors.with_opacity(0.45, _S_BORDER)),
        content=ft.Row(
            spacing=Spacing.md,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                _icon_badge(ft.icons.VERIFIED_USER_ROUNDED, _S_CYAN),
                ft.Column(
                    spacing=3,
                    expand=True,
                    controls=[
                        ft.Text("Signed in as", size=12, color=_S_MUTED),
                        ft.Text(
                            f"{user.full_name} ({user.email})",
                            size=14,
                            weight=ft.FontWeight.W_600,
                            color=_S_TEXT,
                        ),
                    ],
                ),
            ],
        ),
    )

    sign_out_btn = _settings_button(
        "Sign out",
        on_click=on_logout,
        icon=ft.icons.LOGOUT_ROUNDED,
        kind="danger",
    )

    body = ft.Row(
        spacing=Spacing.md,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
        controls=[
            session_panel,
            ft.Container(content=sign_out_btn),
        ],
    )

    return build_settings_card(
        title="Session / Security",
        subtitle="End this browser session when you are done working.",
        icon=ft.icons.SHIELD_ROUNDED,
        accent=_S_DANGER,
        content=[body],
    )


# ---------- UI primitives ----------


def _icon_badge(icon: str, accent: str) -> ft.Control:
    return ft.Container(
        width=42,
        height=42,
        border_radius=14,
        alignment=ft.alignment.center,
        bgcolor=ft.colors.with_opacity(0.12, accent),
        border=ft.border.all(1, ft.colors.with_opacity(0.38, accent)),
        content=ft.Icon(icon, size=20, color=accent),
    )


def _pill_badge(label: str, color: str) -> ft.Control:
    return ft.Container(
        bgcolor=ft.colors.with_opacity(0.12, color),
        border=ft.border.all(1, ft.colors.with_opacity(0.36, color)),
        border_radius=Radii.pill,
        padding=ft.padding.symmetric(horizontal=10, vertical=4),
        content=ft.Text(label, size=11, weight=ft.FontWeight.W_700, color=color),
    )


def _info_callout(title: str, message: str, icon: str) -> ft.Control:
    return ft.Container(
        padding=ft.padding.all(14),
        border_radius=14,
        bgcolor=ft.colors.with_opacity(0.08, _S_CYAN),
        border=ft.border.all(1, ft.colors.with_opacity(0.4, _S_CYAN)),
        content=ft.Row(
            spacing=Spacing.md,
            vertical_alignment=ft.CrossAxisAlignment.START,
            controls=[
                ft.Icon(icon, size=20, color=_S_CYAN),
                ft.Column(
                    spacing=4,
                    expand=True,
                    controls=[
                        ft.Text(title, size=13, weight=ft.FontWeight.W_700, color=_S_CYAN),
                        ft.Text(message, size=12, color=_S_MUTED),
                    ],
                ),
            ],
        ),
    )


def _settings_button(
    text: str,
    *,
    on_click: Callable[[ft.ControlEvent], None],
    icon: str,
    kind: str = "secondary",
) -> ft.Control:
    styles = {
        "primary": (_S_CYAN, "#06111F", True, _S_CYAN),
        "secondary": (_S_CARD_SOFT, _S_CYAN, False, _S_BORDER),
        "warning": (_S_CARD_SOFT, _S_WARNING, False, _S_WARNING),
        "danger": (_S_DANGER, "#1A0A0C", True, ft.colors.with_opacity(0.55, _S_DANGER)),
    }
    accent, fg, filled, border_c = styles.get(kind, styles["secondary"])
    bg = accent if filled else ft.colors.with_opacity(0.1, accent)
    border_color = border_c if not filled else ft.colors.with_opacity(0.5, accent)

    return ft.Container(
        height=40,
        border_radius=12,
        bgcolor=bg,
        border=ft.border.all(1, border_color),
        padding=ft.padding.symmetric(horizontal=16, vertical=8),
        alignment=ft.alignment.center,
        ink=True,
        on_click=on_click,
        content=ft.Row(
            tight=True,
            spacing=8,
            controls=[
                ft.Icon(icon, size=16, color=fg),
                ft.Text(text, size=13, weight=ft.FontWeight.W_700, color=fg),
            ],
        ),
    )


def _user_initials(user: User) -> str:
    parts = (user.full_name or user.username or "U").split()
    if len(parts) >= 2:
        return (parts[0][0] + parts[-1][0]).upper()
    return (parts[0][:2] if parts[0] else "U").upper()


def _provider_label(user: User) -> str:
    provider = (getattr(user, "provider", None) or "").strip().lower()
    if provider == "google" or getattr(user, "google_id", None):
        return "Google"
    return "Email"
