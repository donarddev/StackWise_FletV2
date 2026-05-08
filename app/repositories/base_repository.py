"""BaseRepository — every repository injects DatabaseService here.

Repositories must NOT contain business logic. They translate between the
database row format and entity models.
"""

from __future__ import annotations

from app.services.database_service import DatabaseService


class BaseRepository:
    def __init__(self, database: DatabaseService) -> None:
        self.db = database
