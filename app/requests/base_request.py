"""Base request class — common validation infrastructure.

Subclasses implement ``rules()`` and ``sanitize()``; the base class
collects errors and exposes a clean ``validate() -> dict[field, msg]`` API.

Request classes contain *no* business logic — they only validate and
sanitize input before it reaches a service.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable


Rule = tuple[str, Callable[[Any], bool], str]
"""(field_name, predicate, error_message)"""


@dataclass
class BaseRequest:
    """All requests inherit from this and must be dataclasses."""

    errors: dict[str, str] = field(default_factory=dict, init=False, repr=False)

    # ---------- subclass hooks ----------

    def rules(self) -> list[Rule]:
        return []

    def sanitize(self) -> None:
        """Override to mutate fields in-place before validation."""

    # ---------- public API ----------

    def is_valid(self) -> bool:
        return self.validate() == {}

    def validate(self) -> dict[str, str]:
        self.errors.clear()
        self.sanitize()
        for field_name, predicate, message in self.rules():
            if field_name in self.errors:
                continue  # first error wins per field
            try:
                value = getattr(self, field_name)
            except AttributeError:
                self.errors[field_name] = "Field not provided."
                continue
            if not predicate(value):
                self.errors[field_name] = message
        return dict(self.errors)

    def first_error(self) -> str | None:
        if not self.errors:
            return None
        return next(iter(self.errors.values()))
