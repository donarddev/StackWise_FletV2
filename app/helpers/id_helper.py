"""ID generation helpers."""

from __future__ import annotations

import uuid


def new_uuid() -> str:
    return uuid.uuid4().hex
