"""Database service.

MySQL/MariaDB-backed database service using PyMySQL. Repositories go
through this service so the rest of the app stays driver-agnostic.

Hard guarantees enforced by this module:

  * It will **never** modify a forbidden database (see ``FORBIDDEN_DATABASES``
    in ``app.config.database_config``). The check fires at config-time and
    again before every CREATE DATABASE / migration step.
  * It will **never** issue ``DROP DATABASE``, ``DROP TABLE``, or
    ``TRUNCATE`` — schema changes are append-only via ``CREATE TABLE
    IF NOT EXISTS`` in ``database/migrations/``.
  * Auto-creation of the configured database can be opted out via the
    ``STACKWISE_DB_AUTO_CREATE=false`` environment variable. With auto-create
    off, the service requires the database to already exist (created via
    phpMyAdmin or ``database/setup.sql``).
"""

from __future__ import annotations

from threading import RLock
from typing import Any, Iterable, Optional, Sequence

import pymysql
from pymysql.connections import Connection
from pymysql.cursors import DictCursor

from app.config.database_config import DatabaseConfig
from app.utils.logger import get_logger

log = get_logger(__name__)


class DatabaseService:
    def __init__(self, config: DatabaseConfig) -> None:
        # Re-assert safety here too — defense in depth, in case a caller
        # bypasses the dataclass constructor (e.g. via __setattr__).
        config.assert_safe_to_modify()

        self._config = config
        self._connection: Optional[Connection] = None
        self._lock = RLock()

    # ---------- lifecycle ----------

    def connect(self) -> None:
        if self._connection is not None:
            return

        if self._config.driver not in {"mysql", "mariadb"}:
            raise NotImplementedError(
                f"Driver '{self._config.driver}' is not supported. "
                "Set STACKWISE_DB_DRIVER=mysql for Laragon/phpMyAdmin."
            )

        if self._config.auto_create_database:
            self._ensure_database_exists()
        else:
            self._assert_database_exists()

        self._connection = self._open()
        log.info(
            "MySQL connected: %s@%s:%s/%s",
            self._config.user, self._config.host, self._config.port, self._config.database,
        )

        from database.migrations.initial_migration import run_migrations
        run_migrations(self)

        from database.seeders.learning_content_seeder import seed_learning_content
        seed_learning_content(self)

    def close(self) -> None:
        with self._lock:
            if self._connection is not None:
                try:
                    self._connection.close()
                except Exception:
                    pass
                self._connection = None

    # ---------- query API ----------

    def execute(self, sql: str, params: Sequence[Any] | None = None) -> int:
        """Execute a write statement and return the lastrowid (0 for non-INSERTs)."""
        with self._lock:
            self._ensure_alive()
            assert self._connection is not None
            with self._connection.cursor() as cur:
                cur.execute(sql, tuple(params or ()))
                return int(cur.lastrowid or 0)

    def executemany(self, sql: str, seq: Iterable[Sequence[Any]]) -> None:
        with self._lock:
            self._ensure_alive()
            assert self._connection is not None
            with self._connection.cursor() as cur:
                cur.executemany(sql, [tuple(p) for p in seq])

    def fetch_one(self, sql: str, params: Sequence[Any] | None = None) -> Optional[dict]:
        with self._lock:
            self._ensure_alive()
            assert self._connection is not None
            with self._connection.cursor() as cur:
                cur.execute(sql, tuple(params or ()))
                return cur.fetchone()

    def fetch_all(self, sql: str, params: Sequence[Any] | None = None) -> list[dict]:
        with self._lock:
            self._ensure_alive()
            assert self._connection is not None
            with self._connection.cursor() as cur:
                cur.execute(sql, tuple(params or ()))
                return list(cur.fetchall())

    def script(self, sql: str) -> None:
        """Execute a multi-statement DDL script.

        Asserts the configured database is safe to modify before each call,
        so even a misconfigured caller can't sneak DDL onto a forbidden DB.
        """
        self._config.assert_safe_to_modify()
        with self._lock:
            self._ensure_alive()
            assert self._connection is not None
            with self._connection.cursor() as cur:
                for statement in _split_statements(sql):
                    if statement.strip():
                        cur.execute(statement)

    # ---------- internals ----------

    def _open(self, *, with_database: bool = True) -> Connection:
        kwargs: dict[str, Any] = dict(
            host=self._config.host,
            port=self._config.port,
            user=self._config.user,
            password=self._config.password,
            charset=self._config.charset,
            autocommit=True,
            cursorclass=DictCursor,
        )
        if with_database:
            kwargs["database"] = self._config.database
        try:
            return pymysql.connect(**kwargs)
        except pymysql.MySQLError as exc:
            target = (
                f"{self._config.user}@{self._config.host}:{self._config.port}"
                + (f"/{self._config.database}" if with_database else "")
            )
            raise RuntimeError(
                f"Could not connect to MySQL ({target}). "
                f"Is Laragon running and MySQL started? Original error: {exc}"
            ) from exc

    def _ensure_database_exists(self) -> None:
        """Create the configured database if it doesn't exist yet.

        Will refuse outright if the configured database is on the forbidden
        list — and uses ``CREATE DATABASE IF NOT EXISTS`` so it is a no-op
        when the database already exists (which is the normal case here).
        """
        self._config.assert_safe_to_modify()

        boot = self._open(with_database=False)
        try:
            with boot.cursor() as cur:
                cur.execute(
                    f"CREATE DATABASE IF NOT EXISTS `{self._config.database}` "
                    "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
                )
        finally:
            boot.close()

    def _assert_database_exists(self) -> None:
        """Verify the configured DB exists when auto-create is disabled."""
        boot = self._open(with_database=False)
        try:
            with boot.cursor() as cur:
                cur.execute(
                    "SELECT SCHEMA_NAME FROM information_schema.SCHEMATA "
                    "WHERE SCHEMA_NAME = %s LIMIT 1",
                    (self._config.database,),
                )
                row = cur.fetchone()
                if not row:
                    raise RuntimeError(
                        f"Database `{self._config.database}` does not exist and "
                        "STACKWISE_DB_AUTO_CREATE=false. Create it in phpMyAdmin "
                        "(or run database/setup.sql) and try again."
                    )
        finally:
            boot.close()

    def _ensure_alive(self) -> None:
        if self._connection is None:
            raise RuntimeError("DatabaseService is not connected. Call connect() first.")
        try:
            self._connection.ping(reconnect=True)
        except Exception as exc:
            log.warning("Lost MySQL connection (%s) — reconnecting.", exc)
            self._connection = self._open()


def _split_statements(sql: str) -> list[str]:
    """Naive but sufficient SQL splitter for our migration DDL."""
    parts: list[str] = []
    buf: list[str] = []
    for line in sql.splitlines():
        buf.append(line)
        if line.rstrip().endswith(";"):
            parts.append("\n".join(buf))
            buf = []
    if buf:
        parts.append("\n".join(buf))
    return parts
