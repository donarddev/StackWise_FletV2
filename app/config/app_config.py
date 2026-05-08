"""Top-level application configuration.

All runtime configuration values live here, sourced from environment variables
with sane defaults. This is the only module that should read os.environ
directly, keeping the rest of the codebase free of environment coupling.
"""

from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class AppConfig:
    app_name: str = "StackWise AI"
    app_tagline: str = "AI-Powered Decision Support for Modern Software Teams"
    version: str = "1.0.0"

    window_width: int = 1440
    window_height: int = 900
    window_min_width: int = 1100
    window_min_height: int = 720

    log_level: str = os.getenv("STACKWISE_LOG_LEVEL", "INFO")

    session_timeout_minutes: int = 60 * 24


def get_app_config() -> AppConfig:
    return AppConfig()
