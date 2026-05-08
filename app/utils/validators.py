"""Generic, framework-free validators reused by request classes."""

from __future__ import annotations

import re
from typing import Iterable

EMAIL_REGEX = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")
USERNAME_REGEX = re.compile(r"^[A-Za-z0-9_.\-]{3,32}$")


def is_email(value: str) -> bool:
    return bool(value) and EMAIL_REGEX.match(value) is not None


def is_username(value: str) -> bool:
    return bool(value) and USERNAME_REGEX.match(value) is not None


def is_non_empty(value: object) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return value.strip() != ""
    return True


def is_in(value: object, allowed: Iterable) -> bool:
    return value in set(allowed)


def min_length(value: str, n: int) -> bool:
    return isinstance(value, str) and len(value) >= n


def max_length(value: str, n: int) -> bool:
    return isinstance(value, str) and len(value) <= n


def sanitize(value: str) -> str:
    """Strip whitespace and collapse internal whitespace runs."""
    if not isinstance(value, str):
        return value
    return re.sub(r"\s+", " ", value).strip()
