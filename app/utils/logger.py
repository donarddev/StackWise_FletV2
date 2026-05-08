"""Centralized logging factory.

Use ``get_logger(__name__)`` everywhere instead of ``logging.getLogger``
so configuration is consistent across the app.
"""

from __future__ import annotations

import logging
import sys
from logging import Logger

from app.config.app_config import get_app_config

_INITIALIZED = False


def _initialize_root() -> None:
    global _INITIALIZED
    if _INITIALIZED:
        return

    cfg = get_app_config()
    root = logging.getLogger()
    root.setLevel(cfg.log_level)

    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)-7s | %(name)-30s | %(message)s",
        datefmt="%H:%M:%S",
    )
    handler.setFormatter(formatter)

    root.handlers.clear()
    root.addHandler(handler)
    _INITIALIZED = True


def get_logger(name: str) -> Logger:
    _initialize_root()
    return logging.getLogger(name)
