"""StackWise AI — application entrypoint.

Bootstraps configuration, the dependency-injection container, the router,
and the Flet page. Keep this file *thin* — feature work belongs in
controllers/services, not here.
"""

from __future__ import annotations

import os
from pathlib import Path

import flet as ft
from dotenv import load_dotenv

# Load environment variables from project-root .env as early as possible.
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

# Keep Flet's built-in OAuth handler from intercepting this app's Google callback.
os.environ["FLET_OAUTH_CALLBACK_HANDLER_ENDPOINT"] = "flet_oauth_callback"

# Safe temporary debug output (no secret values are printed)
print("GOOGLE_CLIENT_ID loaded:", bool(os.getenv("GOOGLE_CLIENT_ID")))
print("GOOGLE_CLIENT_SECRET loaded:", bool(os.getenv("GOOGLE_CLIENT_SECRET")))
print("GOOGLE_REDIRECT_URI loaded:", os.getenv("GOOGLE_REDIRECT_URI"))

from app.config.app_config import get_app_config
from app.core.container import Container
from app.core.router import Router
from app.utils.logger import get_logger
from ui.themes.app_theme import Colors, build_flet_theme

log = get_logger(__name__)


def main(page: ft.Page) -> None:
    cfg = get_app_config()

    page.title = f"{cfg.app_name} — {cfg.app_tagline}"
    page.bgcolor = Colors.background
    page.theme_mode = ft.ThemeMode.DARK
    page.theme = build_flet_theme()
    page.fonts = {"Inter": "https://rsms.me/inter/inter.css"}
    page.padding = 0
    page.spacing = 0

    page.window.width = cfg.window_width
    page.window.height = cfg.window_height
    page.window.min_width = cfg.window_min_width
    page.window.min_height = cfg.window_min_height
    page.window.bgcolor = Colors.background
    page.window.title_bar_hidden = False
    page.window.resizable = True

    log.info("Booting %s v%s", cfg.app_name, cfg.version)

    container = Container(page=page)
    setattr(page, "_stackwise_container", container)
    _ = container.database  # eagerly run migrations + seeders

    router = Router(page, container)
    setattr(page, "_stackwise_router", router)
    router.attach()
    router.start(page.route)


if __name__ == "__main__":
    # Serve local UI assets (e.g. branding logo) from ./assets
    ft.app(target=main, assets_dir="assets")
