"""Tests for the database safety guard.

These tests do NOT require a running MySQL server — they only verify that
the configuration-level safety stop fires whenever someone tries to point
StackWise AI at the protected `stackwise` (Laravel) database.
"""

from __future__ import annotations

import unittest

from app.config.database_config import (
    FORBIDDEN_DATABASES,
    DatabaseConfig,
    SAFETY_STOP_MESSAGE,
    is_forbidden_database,
)


class DatabaseSafetyTests(unittest.TestCase):
    def test_forbidden_set_contains_stackwise(self) -> None:
        self.assertIn("stackwise", FORBIDDEN_DATABASES)

    def test_is_forbidden_database_is_case_insensitive(self) -> None:
        self.assertTrue(is_forbidden_database("stackwise"))
        self.assertTrue(is_forbidden_database("STACKWISE"))
        self.assertTrue(is_forbidden_database("  StackWise  "))
        self.assertFalse(is_forbidden_database("stackwise_ai"))
        self.assertFalse(is_forbidden_database("stackwise_ai_test"))

    def test_config_raises_for_forbidden_database(self) -> None:
        with self.assertRaises(RuntimeError) as ctx:
            DatabaseConfig(
                driver="mysql",
                host="localhost",
                port=3306,
                user="root",
                password="",
                database="stackwise",
            )
        self.assertIn("Safety stop", str(ctx.exception))
        self.assertIn("stackwise", str(ctx.exception))

    def test_config_raises_for_uppercase_forbidden_database(self) -> None:
        with self.assertRaises(RuntimeError):
            DatabaseConfig(
                driver="mysql",
                host="localhost",
                port=3306,
                user="root",
                password="",
                database="STACKWISE",
            )

    def test_config_accepts_stackwise_ai(self) -> None:
        cfg = DatabaseConfig(
            driver="mysql",
            host="localhost",
            port=3306,
            user="root",
            password="",
            database="stackwise_ai",
        )
        self.assertEqual(cfg.database, "stackwise_ai")
        cfg.assert_safe_to_modify()

    def test_safety_message_format(self) -> None:
        msg = SAFETY_STOP_MESSAGE.format(name="stackwise")
        self.assertIn("Safety stop", msg)
        self.assertIn("Laravel", msg)


if __name__ == "__main__":
    unittest.main()
