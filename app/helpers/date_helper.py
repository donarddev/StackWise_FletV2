"""Date and timestamp formatting helpers."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def to_iso(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).replace(microsecond=0).isoformat()


def from_iso(value: str) -> datetime:
    return datetime.fromisoformat(value)


def from_db(value: Any) -> datetime:
    """Convert a value coming back from the database into a ``datetime``.

    MySQL/MariaDB drivers return ``datetime`` objects natively. SQLite
    returns ``"YYYY-MM-DD HH:MM:SS"`` strings. This helper accepts both so
    the rest of the codebase stays driver-agnostic.
    """
    if isinstance(value, datetime):
        return value if value.tzinfo else value.replace(tzinfo=timezone.utc)
    if isinstance(value, str):
        return from_iso(value.replace(" ", "T"))
    raise TypeError(f"Cannot convert {type(value).__name__} to datetime")


def humanize(dt: datetime) -> str:
    """Return a short, human-friendly timestamp (e.g. '5m ago', 'Yesterday')."""
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    delta = now_utc() - dt
    seconds = int(delta.total_seconds())

    if seconds < 60:
        return "Just now"
    minutes = seconds // 60
    if minutes < 60:
        return f"{minutes}m ago"
    hours = minutes // 60
    if hours < 24:
        return f"{hours}h ago"
    days = hours // 24
    if days == 1:
        return "Yesterday"
    if days < 7:
        return f"{days}d ago"
    return dt.strftime("%b %d, %Y")
