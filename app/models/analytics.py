"""Analytics datapoint."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Mapping

from app.helpers.date_helper import from_db


@dataclass
class AnalyticsPoint:
    id: int
    user_id: int
    metric: str
    value: float
    metadata: dict = field(default_factory=dict)
    recorded_at: datetime = field(default_factory=datetime.now)

    @staticmethod
    def from_row(row: Mapping[str, Any]) -> "AnalyticsPoint":
        return AnalyticsPoint(
            id=int(row["id"]),
            user_id=int(row["user_id"]),
            metric=row["metric"],
            value=float(row["value"]),
            metadata=json.loads(row["metadata_json"] or "{}") if row["metadata_json"] else {},
            recorded_at=from_db(row["recorded_at"]),
        )
