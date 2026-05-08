"""Database configuration.

Defaults are tuned for **Laragon's** out-of-the-box MySQL:

  * host:     localhost
  * port:     3306
  * user:     root
  * password: (empty)
  * database: stackwise_ai

This module also enforces a **safety guard** so the application can never
accidentally connect to a database name the user has explicitly reserved
for another project (e.g. ``stackwise`` belongs to a Laravel app).
"""

from __future__ import annotations

import os
from dataclasses import dataclass


# ---------------------------------------------------------------------------
# Safety guard
# ---------------------------------------------------------------------------

# Database names the application will refuse to touch under any circumstance.
# The check is case-insensitive and runs the moment a DatabaseConfig is built,
# so no migration, query, or connection can sneak past it.
FORBIDDEN_DATABASES: frozenset[str] = frozenset({"stackwise"})

SAFETY_STOP_MESSAGE = (
    "Safety stop: The `{name}` database belongs to the Laravel project "
    "and must not be modified.\n"
    "Set STACKWISE_DB_NAME to a different database (default: 'stackwise_ai')."
)


def is_forbidden_database(name: str) -> bool:
    return (name or "").strip().lower() in FORBIDDEN_DATABASES


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class DatabaseConfig:
    driver: str = os.getenv("STACKWISE_DB_DRIVER", "mysql")
    host: str = os.getenv("STACKWISE_DB_HOST", "localhost")
    port: int = int(os.getenv("STACKWISE_DB_PORT", "3306"))
    user: str = os.getenv("STACKWISE_DB_USER", "root")
    password: str = os.getenv("STACKWISE_DB_PASSWORD", "")
    database: str = os.getenv("STACKWISE_DB_NAME", "stackwise_ai")
    charset: str = os.getenv("STACKWISE_DB_CHARSET", "utf8mb4")
    auto_create_database: bool = (
        os.getenv("STACKWISE_DB_AUTO_CREATE", "true").lower() == "true"
    )

    # ---------- safety ----------

    def __post_init__(self) -> None:
        # Hard-stop the moment a forbidden database name is configured.
        # This fires *before* anything else can happen with this config.
        self.assert_safe_to_modify()

    def assert_safe_to_modify(self) -> None:
        """Raise immediately if this config would touch a forbidden database."""
        if is_forbidden_database(self.database):
            raise RuntimeError(SAFETY_STOP_MESSAGE.format(name=self.database))


def get_database_config() -> DatabaseConfig:
    return DatabaseConfig()
