"""Analytics repository.

Stores arbitrary numeric metrics keyed by user. Useful as a sink for
tracking events the dashboard summarizes.
"""

from __future__ import annotations

import json

from app.models.analytics import AnalyticsPoint
from app.repositories.base_repository import BaseRepository


class AnalyticsRepository(BaseRepository):
    def record(
        self,
        user_id: int,
        metric: str,
        value: float,
        metadata: dict | None = None,
    ) -> None:
        self.db.execute(
            "INSERT INTO analytics (user_id, metric, value, metadata_json) "
            "VALUES (%s, %s, %s, %s)",
            (user_id, metric, float(value), json.dumps(metadata or {})),
        )

    def list_for_user(self, user_id: int, metric: str | None = None) -> list[AnalyticsPoint]:
        if metric:
            rows = self.db.fetch_all(
                "SELECT * FROM analytics WHERE user_id = %s AND metric = %s "
                "ORDER BY recorded_at DESC",
                (user_id, metric),
            )
        else:
            rows = self.db.fetch_all(
                "SELECT * FROM analytics WHERE user_id = %s ORDER BY recorded_at DESC",
                (user_id,),
            )
        return [AnalyticsPoint.from_row(r) for r in rows]
